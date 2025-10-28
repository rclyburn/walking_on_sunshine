import click

from walking_on_sunshine.app.app import App
from walking_on_sunshine.command.root import root_cmd
from walking_on_sunshine.common.logging.logger import get_logger

logger = get_logger(__name__)


@root_cmd.command()
@click.pass_context
@click.option("--album_name", prompt="Please enter your album name")
@click.option("--start_address", prompt="Please enter your starting address")
def start(ctx: click.Context, album_name: str, start_address: str):
    root_cfg = ctx.obj["root_cfg"]
    app = App(root_cfg.app)

    app.run(album_name, start_address)
