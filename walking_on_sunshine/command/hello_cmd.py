import click

from walking_on_sunshine.command.root import root_cmd
from walking_on_sunshine.common.logging.logger import get_logger

logger = get_logger(__name__)


@root_cmd.command()
@click.pass_context
def hello(ctx: click.Context):
    root_cfg = ctx.obj["root_cfg"]
    logger.info(root_cfg)
    logger.debug("Debug message")
