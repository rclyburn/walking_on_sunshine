import click

from walking_on_sunshine.command.root import root_cmd
from walking_on_sunshine.common.logging.logger import get_logger

logger = get_logger(__name__)


@root_cmd.command()
@click.pass_context
def hello(ctx: click.Context):
    foo = ctx.obj["foo"]
    logger.info(foo)
    logger.debug("Debug message")
