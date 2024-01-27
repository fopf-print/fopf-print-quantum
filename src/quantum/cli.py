import click

from quantum.workers import fopf_print_bot_worker


@click.group()
def cli():
    pass


@cli.command()
def run_bot():
    fopf_print_bot_worker()
