import docker
import getpass

import os
import logging
import pkg_resources
from os.path import expanduser

logger = logging.getLogger(__name__)


def start():
    """Starts a container running an ssh-agent. This also will remove an existing container and
    replace it if run again.
    """
    logger.info('Starting ssh-agent')
    client = docker.from_env()
    logger.info('Check for image')
    try:
        client.images.get('ssh-agent')
        logger.info('Image Found')
    except docker.errors.ImageNotFound:
        logger.info('Building Image')
        build_ssh()

    try:
        client.containers.get("ssh-agent").stop()
        client.containers.get("ssh-agent").remove()
    except docker.errors.NotFound:
        pass
    client.containers.run(image="ssh-agent", name="ssh-agent", detach=True)


def add_keys():
    """Tries to add ssh keys found in ~/.ssh/cloud_keys, will prompt with required command if
    there is a password.
    """

    client = docker.from_env()
    config = params()

    try:
        client.containers.run(
            image=config["image"],
            remove=True,
            volumes_from=config["volumes_from"],
            volumes=config["volumes"],
            command="ssh-add /root/.ssh/google_compute_engine",
        )
    except docker.errors.ContainerError:
        logger.warning(
            'google_compute_engine failed to be added, probably needs a password: try running'
        )  # NOQA
        logger.warning(
            'docker run -it --rm --volumes-from=ssh-agent -v ~/.ssh/cloud_keys:/.ssh ssh-agent ssh-add /root/.ssh/google_compute_engine'  # NOQA
        )

    try:
        client.containers.run(
            image=config["image"],
            remove=True,
            volumes_from=config["volumes_from"],
            volumes=config["volumes"],
            command="ssh-add /root/.ssh/id_ed25519",
        )
    except docker.errors.ContainerError:
        logger.warning('id_ed25519 failed to be added, probably needs a password: try running')
        logger.warning(
            'docker run -it --rm --volumes-from=ssh-agent -v ~/.ssh/cloud_keys:/.ssh ssh-agent ssh-add /root/.ssh/id_ed25519'  # NOQA
        )


def shutdown():
    """shutdown ssh-agent
    """
    client = docker.from_env()
    try:
        container = client.containers.get("ssh-agent")
        container.stop()
    except docker.errors.NotFound:
        pass


def params():
    """Generates dictionary containing parameters to run ssh-agent

    Returns
    -------
    dict
        Dictionary containing parameters to run ssh-agent
    """
    environment = {"USER": getpass.getuser(), "SSH_AUTH_SOCK": "/.ssh-agent/socket"}
    volumes_from = ["ssh-agent"]
    volumes = {expanduser("~") + "/.ssh/cloud_keys": {"bind": "/root/.ssh", "mode": "rw"}}
    config = {
        "environment": environment,
        "volumes_from": volumes_from,
        "volumes": volumes,
        "image": "ssh-agent",
    }
    return config


def build_ssh():
    """Build the ssh-agent image
    """
    client = docker.from_env()
    dockerfile = pkg_resources.resource_filename('pydocker', 'Dockerfile.agent')
    path = os.path.dirname(dockerfile)
    for line in client.api.build(
        path=path, tag='ssh-agent', rm=True, dockerfile=dockerfile, decode=True
    ):
        if 'stream' in line:
            print(line['stream'])
