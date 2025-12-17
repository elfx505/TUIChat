import typer
from rich import print

from .user_config import get_host, get_port, set_host, set_port, set_username

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
def chhost(hostname: str):
    """
    Set a new hostname. Changes the user_conf.json config file.
    """

    set_host(hostname)

    print(f"New hostname: [green]{hostname}[/green]")


@app.command()
def chport(port: str):
    """
    Set a new port number. Changes the user_conf.json config file.
    """

    set_port(port)

    print(f"New port number: [green]{port}[/green]")


# pip entry point
def main():
    app()


if __name__ == "__main__":
    app()
