import click
import uvicorn

from quantum import settings
from quantum.core.globals import GlobalValue
from quantum.workers import fopf_print_bot_worker, refill_worker


@click.group()
def cli():
    pass


@cli.command()
@click.option('--port', default=8000)
def run_server(port: int):
    from aiogram import Bot
    from aiogram.enums import ParseMode

    from quantum.web import app

    GlobalValue[Bot].set(Bot(settings.FOPF_PRINT_BOT_TOKEN, parse_mode=ParseMode.HTML))
    uvicorn.run(app, host='0.0.0.0', port=port)


@cli.command()
def run_bot():
    fopf_print_bot_worker()


@cli.command()
def run_refill_worker():
    refill_worker()
