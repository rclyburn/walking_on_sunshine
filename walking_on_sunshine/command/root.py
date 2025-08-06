import logging
from pathlib import Path

import click
import structlog
import yaml
from dotenv import load_dotenv

from walking_on_sunshine.command.config import RootConfig


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

    root_cfg = RootConfig()
    config_path = Path("config.yml")

    if config_path.is_file():
        with config_path.open() as f:
            config_obj = yaml.safe_load(f)
            if config_obj:
                root_cfg = RootConfig.model_validate(config_obj)

    ctx.obj["root_cfg"] = root_cfg

    load_dotenv()
