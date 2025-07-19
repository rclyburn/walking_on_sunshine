import traceback

from walking_on_sunshine.command.root import root_cmd
from walking_on_sunshine.common.logging.logger import get_logger, init_logger


def main():
    init_logger()
    logger = get_logger(__name__)

    try:
        root_cmd()
    except Exception:
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
