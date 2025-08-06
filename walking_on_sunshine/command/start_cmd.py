import click

from walking_on_sunshine.app.album_length import AlbumLength
from walking_on_sunshine.app.app import App
from walking_on_sunshine.command.root import root_cmd
from walking_on_sunshine.common.logging.logger import get_logger

logger = get_logger(__name__)


@root_cmd.command()
@click.pass_context
@click.option("--album_name", prompt="Please enter your album name")
def start(ctx: click.Context, album_name: str):
    root_cfg = ctx.obj["root_cfg"]

    app = App(root_cfg.app)
    length = AlbumLength(app.config.SPOTIFY_CLIENT_ID, app.config.SPOTIFY_CLIENT_SECRET)

    logger.info(length.get_album_length(album_name))
