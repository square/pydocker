from __future__ import print_function
import docker
import os
from os.path import expanduser, abspath, splitext, basename
from pydocker import ssh
import logging
import glob
import getpass
from delegator import run

logger = logging.getLogger(__name__)


def bash(command, environment=""):
    logger.info(command)
    res = run(command, env={"ENVIRONMENT": environment})
    if len(res.out) > 0:
        logger.info(res.out)
    if len(res.err) > 0:
        logger.info(res.err)
    if res.ok is False:
        raise Exception("Bash failed: {}".format(res.err.splitlines()))
    return res.out


def setup_machine():
    """Setup laptop for first use. This includes creating ssh config, and making a copy of credentials.
    """
    client = docker.from_env()
    if client.info().get('ServerVersion') < '18.09.2':
        raise ('Docker server needs to be at least 18.09.2')
    ssh_path = os.path.join(expanduser('~'), '.ssh')
    cloud_path = os.path.join(ssh_path, 'cloud_keys')
    config_path = os.path.join(cloud_path, 'config')
    bash('mkdir -p {}'.format(cloud_path))
    bash('cp ~/.ssh/config ~/.ssh/{}/config'.format('cloud_keys'))
    bash("sed -i '' '/.*UseKeychain.*/d' ~/.ssh/cloud_keys/config")
    bash("sed -i '' '/.*ControlPath .*/d' ~/.ssh/cloud_keys/config")

    config = """
    Host *
        ControlPath /tmp/master-%r@%h:%p
        User {}
    """.format(
        getpass.getuser()
    )
    with open(config_path, 'r') as h:
        conents = h.read()
    with open(config_path, 'w') as h:
        h.write(config)
    with open(config_path, 'a') as h:
        h.write(conents)
    keys = [splitext(x)[0] for x in glob.glob(os.path.join(ssh_path, '*.pub'))]
    for key in keys:
        logger.info('Adding key {}'.format(key))
        dest = os.path.join(cloud_path, basename(key))
        if os.path.lexists(dest) is False:
            bash('cp {} {}'.format(key, dest))


def start_ssh():
    try:
        logger.info("Starting ssh-agent and loading keys")
        ssh.start()
        ssh.add_keys()
    except docker.errors.APIError as e:
        print(e)


class LocalContainer:
    def __init__(
        self,
        image,
        name,
        working_dir,
        port,
        logs=False,
        command='jupyter notebook --ip=0.0.0.0 --allow-root --NotebookApp.token=""',
        **kwargs
    ):
        """Setup local container with users gcloud credentials, and ssh-agent.

        Parameters
        ----------
        image : str
            docker image to use
        name : str
            Pick container name
        working_dir : str
            Path that you want mounted in container
        port : int
            Port mapped to host machine (laptop)
        logs : bool, optional
            Show container logs (the default is False)
        command : str, optional
            Command to be run on startup (the default is
            'jupyter notebook --ip=0.0.0.0 --allow-root --NotebookApp.token=""'s])

        """
        self.image = image
        self.name = name
        self.working_dir = working_dir
        self.port = port
        self.client = docker.from_env()
        self.logs = logs
        self.command = command
        try:
            self.client.images.get(image)
            logger.info("Using local image")
        except docker.errors.ImageNotFound:
            logger.info("Image not found, pulling")
            last_status = None
            if len(image.split(':')) == 1:
                tag = 'latest'
                repository = image
            else:
                repository, tag = image.split(':')
            for line in self.client.api.pull(repository, tag, stream=True, decode=True):
                status = line.get('status')
                progress = line.get('progress')
                if status is not None and status != last_status:
                    print(status)
                    last_status = status
                if progress is not None:
                    print(progress, end='\r')

        # Setup enviroment variables, etc for container
        self.config = ssh.params()
        self.environment = self.config["environment"]
        self.environment["CLOUD"] = False
        self.environment["DOCKER"] = 'true'

        # Mount user gcloud credentials
        self.volumes = self.config["volumes"]

        # Mount working directory
        self.volumes[abspath(expanduser(working_dir))] = {
            "bind": "/current/working_dir/",
            "mode": "rw",
        }

    def gcloud(self):
        import google.auth

        _, project = google.auth.default()
        if project is None:
            raise ValueError("google.auth.default() could not determine cloud project on laptop")

        self.environment["GOOGLE_CLOUD_PROJECT"] = project
        self.environment[
            "GOOGLE_APPLICATION_CREDENTIALS"
        ] = '/root/.config/gcloud/application_default_credentials.json'
        self.volumes[expanduser("~") + "/.config/gcloud"] = {
            "bind": "/root/.config/gcloud",
            "mode": "rw",
        }

    def run(self):
        logger.info("Starting docker container")
        try:
            output = self.client.containers.run(
                image=self.image,
                name=self.name,
                command=self.command,
                environment=self.environment,
                volumes=self.volumes,
                volumes_from=self.config["volumes_from"],
                tty=False,
                stderr=True,
                stdout=True,
                detach=True,
                ports={'8888/tcp': self.port},
            )
        except docker.errors.NotFound:
            self.environment.pop('SSH_AUTH_SOCK')
            output = self.client.containers.run(
                image=self.image,
                name=self.name,
                command=self.command,
                environment=self.environment,
                volumes=self.volumes,
                tty=False,
                stderr=True,
                stdout=True,
                detach=True,
                ports={'8888/tcp': self.port},
            )
        if self.logs:
            for log in output.logs(stream=True):
                print(log.rstrip())
