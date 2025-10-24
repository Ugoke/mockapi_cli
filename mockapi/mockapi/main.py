import os
import shutil
import subprocess
import sys
import click
import json
from pathlib import Path


from ..mockapi.settings import HOST, PORT
from ..mockapi.messages import HELP_TEXT_FOR_ADD_COMMAND, HELP_TEXT_FOR_ADD_SETTINGS_COMMAND, HELP_TEXT_FOR_START_COMMAND, HELP_TEXT_FOR_SET_DEFAULT
from ..core.io.constants import MOCKS_FILE_PATH, SETTINGS_FILE_PATH, MOCKS_FILE_EXAMPLE_PATH ,SETTINGS_FILE_EXAMPLE_PATH


@click.group()
def cli():
    pass


@cli.command(help=HELP_TEXT_FOR_ADD_COMMAND)
@click.argument("user_file", type=click.Path(exists=True, dir_okay=False, readable=True))
def add(user_file: Path) -> None:
    """Copy user JSON file into mocks.json."""
    user_path = Path(user_file)

    try:
        with open(user_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            click.echo("❌ JSON must be an array of mock objects")
            return
    except json.JSONDecodeError:
        click.echo("❌ File contains invalid JSON")
        return

    shutil.copyfile(user_path, MOCKS_FILE_PATH)
    click.echo(f"✅ {user_file} successfully copied to {MOCKS_FILE_PATH}")


@cli.command(help=HELP_TEXT_FOR_ADD_SETTINGS_COMMAND)
@click.argument("user_file", type=click.Path(exists=True, dir_okay=False, readable=True))
def add_settings(user_file: Path) -> None:
    """Copy user JSON file into settings.json."""
    user_path = Path(user_file)

    try:
        with open(user_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            click.echo("❌ JSON must be a dict")
            return
    except json.JSONDecodeError:
        click.echo("❌ File contains invalid JSON")
        return

    shutil.copyfile(user_path, SETTINGS_FILE_PATH)
    click.echo(f"✅ {user_file} successfully copied to {SETTINGS_FILE_PATH}")


@cli.command(help=HELP_TEXT_FOR_START_COMMAND)
@click.option("--file", "json_file", default=str(MOCKS_FILE_PATH), type=click.Path(exists=True, dir_okay=False, readable=True))
def start(json_file) -> None:
    """Start Django server serving mocks from the given JSON file."""
    click.echo(f"🚀 Starting server with mocks from {json_file}...")

    os.environ["MOCKS_FILE"] = str(Path(json_file).resolve())
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mockapi.django_service.django_service.settings")

    try:
        subprocess.run([sys.executable, "-m", "django", "runserver", f"{HOST}:{PORT}"])
    except KeyboardInterrupt:
        click.echo("\n🛑 Server stopped by user")


@cli.command(help=HELP_TEXT_FOR_SET_DEFAULT)
@click.option("--file-name", "-f", default=None, type=click.STRING)
def set_default(file_name: str) -> None:
    """Set default data JSON files."""
    user_opinion = input("Confirm your action (type YES to continue): ")
    if user_opinion.strip().upper() != "YES":
        click.echo(f"{user_opinion}, this is not YES. Change canceled.")
        return

    try:
        if file_name:
            if file_name == "settings":
                shutil.copyfile(SETTINGS_FILE_EXAMPLE_PATH, SETTINGS_FILE_PATH)
                click.echo("Default settings restored.")
            elif file_name == "mocks":
                shutil.copyfile(MOCKS_FILE_EXAMPLE_PATH, MOCKS_FILE_PATH)
                click.echo("Default mocks restored.")
            else:
                click.echo('You must specify either "settings" or "mocks".')
                return
        else:
            shutil.copyfile(SETTINGS_FILE_EXAMPLE_PATH, SETTINGS_FILE_PATH)
            shutil.copyfile(MOCKS_FILE_EXAMPLE_PATH, MOCKS_FILE_PATH)
            click.echo("Default settings and mocks restored.")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}")
    except Exception as e:
        click.echo(f"Unexpected error: {e}")