import logging
import os
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

    load_dotenv()

    root_cfg = RootConfig()
    config_path = Path("config.yml")

    if config_path.is_file():
        text = os.path.expandvars(config_path.read_text())
        config_obj = yaml.safe_load(text)
        if config_obj:
            root_cfg = RootConfig.model_validate(config_obj)

    ctx.obj["root_cfg"] = root_cfg
