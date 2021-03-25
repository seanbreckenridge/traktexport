import json
from pathlib import Path

import click
from trakt import init  # type: ignore[import]

from .export import export
from .dal import parse_export


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


@main.command(name="inspect")
@click.argument("EXPORT_FILE", type=click.Path(exists=True))
def _inspect(export_file: str) -> None:
    """
    Given an export JSON file, this parses the info into python objects
    """
    data = parse_export(Path(export_file))
    click.secho("Use 'data' to interact with the parsed TraktExport object", fg="green")

    import IPython  # type: ignore[import]

    IPython.embed()


if __name__ == "__main__":
    main(prog_name="traktexport")
