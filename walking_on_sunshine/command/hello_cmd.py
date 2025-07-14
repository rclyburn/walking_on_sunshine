import os

from walking_on_sunshine.command.root import root_cmd


@root_cmd.command()
def hello():
    print(os.getenv("Foo"))
