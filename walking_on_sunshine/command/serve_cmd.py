import click

from walking_on_sunshine.api.api import API
from walking_on_sunshine.app.app import App
from walking_on_sunshine.command.root import root_cmd


@root_cmd.command()
@click.pass_context
def serve(ctx: click.Context):
    print("Serving API")

    root_cfg = ctx.obj["root_cfg"]

    app = App(root_cfg.app)
    api = API(app)
    api.run()
