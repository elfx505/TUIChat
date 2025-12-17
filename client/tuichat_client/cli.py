import typer

app = typer.Typer()


@app.callback()
def root():
    """
    TUI Chat Client CLI
    """
    pass


@app.command()
def connect():
    """
    Connect to the chat server at the indicated hostname and port address.
    Default host and port are taken from the user_conf.json config file.
    """
    print("Connecting to server...")


# pip entry point
def main():
    app()


if __name__ == "__main__":
    app()
