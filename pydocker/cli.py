from __future__ import print_function
import click
import logging
from pydocker.utils import (
    LocalContainer,
    setup_machine,
    start_ssh,
    stop_container,
    delete_container,
)
from pydocker.status import start_server

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
        click.option("-i", "--image", help="Docker image"),
        click.option("-n", "--name", help="container name"),
        click.option(
            "-d", "--working-dir", default=None, help="host directory to mount"
        ),
        click.option(
            "-p",
            "--port",
            default=8888,
            help="Host port to be connected to container port 8888",
        ),
        click.option(
            "-l",
            "--no-logs",
            flag_value=True,
            help="disable streaming of container logs",
        ),
        click.option(
            "--gcloud/--no-gcloud", default=True, help="include gcloud credentials"
        ),
        click.option(
            "-c", "--command", default=None, help="command which is passed to container"
        ),
        click.option(
            "-r",
            "--rm",
            flag_value=True,
            help="enable auto-removal of the container on daemon side when the container’s process exits",  # NOQA
        ),
    ]
    for option in reversed(options):
        func = option(func)

    return func


@cli.command()
def init(**kwargs):
    click.secho("Initial setup (only run once)", bold=True, blink=False)
    setup_machine()


@cli.command()
def agent():
    start_ssh()


@cli.command()
@click.argument("name")
def remove(name):
    delete_container(name)


@cli.command()
def remove_all():
    delete_container()


@cli.command()
@click.argument("name", default=None)
def stop(name):
    stop_container(name)


@cli.command()
def stop_all():
    stop_container()


@cli.command()
@common_options
def launch(**kwargs):
    click.secho(
        "Port forwarded to {}".format(kwargs["port"]),
        fg="magenta",
        bold=True,
        blink=True,
    )
    if kwargs.get("no_logs"):
        kwargs["logs"] = False
    container = LocalContainer(**kwargs)
    if kwargs["gcloud"]:
        container.gcloud()
    container.run()


@cli.command()
@common_options
def status(**kwargs):
    start_server()


if __name__ == "__main__":
    cli()
