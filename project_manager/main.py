"""
Automatically span a matrix of configurations using the `build` command.
Then execute each pipeline using `run`.
And finally aggregate the obtained results using the `gather` command.
"""

import click


@click.group()
def cli() -> None:
    """Automate multi-config simulation runs."""
    pass


@cli.command(help='Setup environments.')
@click.option(
    '--config', '-c', 'config_path', default='config.yaml',
    type=click.Path(exists=True, dir_okay=False), help='Config file to use.')
@click.option(
    '--dry', '-d', default=False, is_flag=True,
    help='Conduct dry run.')
def build(config_path: str, dry: bool) -> None:
    from .commands import build as build_cmd
    build_cmd(config_path, dry)


@cli.command(help='Run simulations in each environment.')
@click.option(
    '--config', '-c', 'config_path', default='config.yaml',
    type=click.Path(exists=True, dir_okay=False), help='Config file to use.')
@click.option(
    '--dry', '-d', default=False, is_flag=True,
    help='Conduct dry run.')
def run(config_path: str, dry: bool) -> None:
    from .commands import run as run_cmd
    run_cmd(config_path, dry)


@cli.command(help='Gather results from each run.')
@click.option(
    '--config', '-c', 'config_path', default='config.yaml',
    type=click.Path(exists=True, dir_okay=False), help='Config file to use.')
@click.option(
    '--output', '-o', default=None,
    type=click.Path(exists=False, file_okay=False),
    help='Path to store aggregated results at.')
def gather(config_path: str, output: str) -> None:
    from .commands import gather as gather_cmd
    gather_cmd(config_path, output)


if __name__ == '__main__':
    cli()
