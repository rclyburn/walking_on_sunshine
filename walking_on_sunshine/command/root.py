import logging

import click
import structlog
from dotenv import load_dotenv


@click.group()
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def root_cmd(ctx: click.Context, verbose: bool):
    ctx.ensure_object(dict)
    if verbose:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )
    else:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        )

    foo = "hello"

    ctx.obj["foo"] = foo

    load_dotenv()
