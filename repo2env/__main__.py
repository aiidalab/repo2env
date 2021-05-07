import json
from dataclasses import asdict

import click

from repo2env import Environment
from repo2env.fetch import fetch_from_url


@click.command()
@click.argument("repository")
@click.option(
    "-d",
    "--dirs",
    type=click.Path(),
    default=[".aiidalab/", "./"],
    help="Relative paths to search within the repository repository.",
    multiple=True,
    show_default=True,
)
@click.option("-v", "--verbose", is_flag=True, help="Increase output verbosity.")
def cli(repository, dirs, verbose):
    """Determine the environment required for a given repository.

    Usage: repo2env /path/to/repository
    """
    with fetch_from_url(repository) as repo:
        for path in (repo.joinpath(dir_) for dir_ in dirs):
            if verbose:
                click.echo(f"Scanning {path} ...", err=True)
            if path.is_dir():
                env = Environment.scan(path)
                click.echo(json.dumps(asdict(env)))
                break
        else:
            raise RuntimeError(f"Unable to parse environment for: {repository}")


if __name__ == "__main__":
    cli()
