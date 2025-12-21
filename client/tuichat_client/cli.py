import typer
from rich import print
from rich.table import Table

from .user_config import (get_host, get_port, load_config, set_host, set_port,
                          set_username)

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


@app.command()
def chuser(username: str):
    """
    Set a new username. Changes the user_conf.json config file.
    """

    set_username(username)
    print(f"New Username: [green]{username}[/green]")


@app.command()
def chaddress(hostname: str, port: str):
    """
    Set a new server address to connect to. Changes the user_conf.json config file.
    """

    set_host(hostname)
    set_port(port)

    print(f"New server address: [green]{hostname}:{port}[/green]")


@app.command()
def conf():
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
