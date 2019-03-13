from __future__ import print_function
import click
import logging
from pydocker.utils import LocalContainer, setup_machine, start_ssh

logging.basicConfig(
    format="%(asctime)s:%(name)s:%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.WARNING,
)
logger = logging.getLogger(__name__)


@click.group()
@click.option("-v", "--verbose", count=True)
def cli(**kwargs):
    verbosity = kwargs["verbose"]
    if verbosity == 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG
    logging.getLogger().setLevel(level)


def common_options(func):
    """ Decorate a subcommand with shared common option group
    """
    options = [
        click.option("-i", "--image", help='Docker image'),
        click.option("-n", "--name", help='container name'),
        click.option("-d", "--working_dir", help='host directory to mount'),
        click.option("-p", "--port", default=8888, help='local port to be connected to container'),
        click.option("-l", "--logs", is_flag=True, help='stream container logs'),
        click.option('--gcloud/--no-gcloud', default=True, help='include gcloud credentials'),
        click.option("-c", "--command", default=None, help='command which is passed to container'),
    ]
    for option in reversed(options):
        func = option(func)

    return func


@cli.command()
def init(**kwargs):
    click.secho('Initial setup (only run once)', bold=True, blink=False)
    setup_machine()


@cli.command()
def agent():
    start_ssh()


@cli.command()
@common_options
def launch(**kwargs):
    click.secho('Port forwarded to {}'.format(kwargs['port']), fg='magenta', bold=True, blink=True)
    container = LocalContainer(**kwargs)
    if kwargs['gcloud']:
        container.gcloud()
    container.run()


if __name__ == "__main__":
    cli()
