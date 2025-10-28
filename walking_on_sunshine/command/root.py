from __future__ import annotations

import logging
import os
from pathlib import Path

import click
import structlog
import yaml
from dotenv import load_dotenv

# If you have a pydantic model for the root config, import it.
# Otherwise you can skip the RootConfig bits and just keep the dict.
try:
    from walking_on_sunshine.command.config import RootConfig  # your model
except Exception:  # pragma: no cover
    RootConfig = None  # type: ignore


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(level),
    )


def _load_config() -> object:
    """
    Load environment, then read config.yml and expand ${VARS},
    then parse into RootConfig (pydantic v2/v1) or return dict.
    """
    # 1) Load env FIRST (Railway service vars, and local .env during dev)
    load_dotenv()

    # 2) Read and expand ${VAR} before YAML parsing
    cfg_path = Path("config.yml")
    data = {}
    if cfg_path.is_file():
        raw = cfg_path.read_text(encoding="utf-8")
        expanded = os.path.expandvars(raw)  # supports $VAR and ${VAR}
        data = yaml.safe_load(expanded) or {}

    # 3) Return the right type
    if RootConfig is None:
        return data
    if hasattr(RootConfig, "model_validate"):  # pydantic v2
        return RootConfig.model_validate(data)
    if hasattr(RootConfig, "parse_obj"):  # pydantic v1
        return RootConfig.parse_obj(data)
    # Fallback if RootConfig is a dataclass or similar
    return RootConfig(**data)  # type: ignore[misc]


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging.")
@click.pass_context
def root_cmd(ctx: click.Context, verbose: bool) -> None:
    """Top-level command group for walking_on_sunshine."""
    _configure_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["root_cfg"] = _load_config()

    # Optional: fail fast if a required env var is missing.
    # Comment out if you prefer lazy failures.
    for required in ("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"):
        if not os.getenv(required):
            logging.error("[boot] Missing required env var: %s", required)
            # Exit non-zero so Railway shows a clear boot failure
            raise SystemExit(1)


# (Optional) If you register subcommands here, keep the import inside
# the function/module scope so it runs after ctx is set up.
# Example:
# try:
#     from .serve_cmd import serve
#     root_cmd.add_command(serve)
# except Exception as e:  # pragma: no cover
#     logging.getLogger(__name__).warning("Could not register 'serve': %s", e)
