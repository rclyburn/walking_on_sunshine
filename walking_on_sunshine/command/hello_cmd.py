from walking_on_sunshine.command.root import root_cmd
from walking_on_sunshine.common.logging.logger_script import get_logger

logger = get_logger(__name__)


@root_cmd.command()
def hello():
    logger.info("Hello world")
    logger.debug("Debug message")
