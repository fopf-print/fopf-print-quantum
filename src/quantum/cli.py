import click
import uvicorn

from quantum.workers import fopf_print_bot_worker, refill_worker


@click.group()
def cli():
    pass


@cli.command()
@click.option('--port', default=8000)
def run_server(port: int):
    from quantum.web import app
    uvicorn.run(app, host='0.0.0.0', port=port)


@cli.command()
def run_bot():
    fopf_print_bot_worker()


@cli.command()
def run_refill_worker():
    refill_worker()
