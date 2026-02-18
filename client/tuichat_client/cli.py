import typer
from rich import print
from rich.table import Table

from .user_config import (
    get_host,
    get_port,
    load_config,
    set_host,
    set_port,
    set_username,
)

from .client import attempt_connect, talk_to_server, update_user_request

app = typer.Typer()


@app.callback()
def root():
    """
    TUI Chat Client CLI
    """
    pass


@app.command()
def connect(
    hostname: str = typer.Option(get_host(), "--hostname", "-h"),
    port: str = typer.Option(get_port(), "--port", "-p"),
):
    """
    Connect to the chat server at the indicated hostname and port address.
    Default host and port are taken from the user_conf.json config file.
    """
    print(f"[green]Connecting to server at [{hostname}:{port}]...[/green]")
    talk_to_server(attempt_connect(get_host(), int(get_port())))


@app.command()
def chuser():
    """
    Set a new username and password for specific host. Changes the user_conf.json config file.
    """

    update_user_request(attempt_connect(get_host(), int(get_port())))


@app.command()
def chaddress(hostname: str, port: str):
    """
    Set a new server address to connect to. Changes the user_conf.json config file.
    """

    set_host(hostname)
    set_port(port)

    print(f"New server address: [green]{hostname}:{port}[/green]")


@app.command()
def status():
    """
    Display the current user configuration found in user_conf.json.
    """
    # Get data
    data = load_config()

    # Create a table
    table = Table(title="\nUser Info")  # Optional title

    # Add columns
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    # Add rows from the dictionary
    for key, value in data.items():
        table.add_row(key, str(value))

    # Print the table
    print(table)


# pip entry point
def main():
    app()


if __name__ == "__main__":
    app()
