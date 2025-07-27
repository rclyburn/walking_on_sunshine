import logging

import click
import structlog
from dotenv import load_dotenv


@click.group()
@click.option("-v", "--verbose", is_flag=True)
def root_cmd(verbose: bool):
    if verbose:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )
    else:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        )

    load_dotenv()
