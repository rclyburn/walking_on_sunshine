import click
from dotenv import load_dotenv




@click.group()
def root_cmd():
    load_dotenv()
