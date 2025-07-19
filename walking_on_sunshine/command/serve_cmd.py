from walking_on_sunshine.api import api
from walking_on_sunshine.command.root import root_cmd


@root_cmd.command()
def serve():
    print("Serving API")
    api.run()
