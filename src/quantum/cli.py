import click

from quantum.workers import fopf_print_bot_worker, refill_worker


@click.group()
def cli():
    pass


@cli.command()
def run_bot():
    fopf_print_bot_worker()


@cli.command()
def run_refill_worker():
    refill_worker()
