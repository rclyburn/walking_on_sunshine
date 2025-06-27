import click
from walking_on_sunshine.command.root import root_cmd
import os


@root_cmd.command()
def hello():
    print(os.getenv("Foo"))
