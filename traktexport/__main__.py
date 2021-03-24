import json

import click
from trakt import init  # type: ignore[import]

from .export import export


@click.group()
def main() -> None:
    """Export data from your Trakt account"""
    pass


@main.command()
@click.argument("USERNAME")
def auth(username: str) -> None:
    """Authenticate (or Re-authenticate) - only needs to be done once"""
    # https://pytrakt.readthedocs.io/en/latest/getstarted.html#oauth-auth
    # use OAuth and store credentials
    init(username, store=True)


@main.command(name="export")
@click.argument("USERNAME")
def _export(username: str) -> None:
    """
    Runs the export - assumes authentication has already been setup

    Prints results to STDOUT
    """
    click.echo(json.dumps(export(username)))


if __name__ == "__main__":
    main(prog_name="traktexport")
