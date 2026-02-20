import os
import socket
from threading import Thread
from rich import print

from .user_config import get_host, get_port, get_username, set_username


def attempt_connect(host: str, port: int) -> socket.socket:
    if not host or not port:
        print("""
        Missing server hostname and/or server port number information!
        Set values with 'tchat host <address> <port_number>'
        """)

        os._exit(
            0
        )  # Needs to provide server address before proceeding. Exit early if they are missing

    try:
        s = socket.socket()
        s.connect((host, port))

    except ConnectionRefusedError as e:
        print(f"Server at {host}:{port} does not exist or is currently offline!")
        os._exit(0)  # Invalid host and/or port. Exit early

    return s


def receive_message(s: socket.socket):
    while True:
        server_message = s.recv(1024).decode()
        if not server_message.strip():
            print("[red]Connection to server closed![/red]")
            os._exit(0)

        print("[blue]" + str(server_message) + "[/blue]")


def send_message(s: socket.socket):
    while True:
        client_input = input("")
        s.sendall(client_input.encode())


def talk_to_server(s: socket.socket):

    password = input("Enter your Password: ")

    # Send Register Message and await response from server
    s.send(f"auth#{get_username()}#{password}".encode())

    Thread(target=receive_message, args=(s,), daemon=True).start()
    send_message(s)


def update_user_request(s: socket.socket):
    try:
        s.settimeout(10.0)

        password = input("Enter your Password: ")

        # Send Update-Credentials Request Message
        s.sendall(f"chuser#{get_username()}#{password}".encode())
        server_message = s.recv(1024).decode("utf-8")

        if server_message.strip() != "AUTH_SUCCESS":
            print(f"[red]Server denied request: {server_message}[/red]")
            return

        print("[green]Authentication successful.[/green]")
        new_username = input("Enter your new Username: ")
        new_password = input("Enter your new Password: ")

        # Send the new credentials
        s.sendall(f"{new_username}#{new_password}".encode())

        final_response = s.recv(1024).decode("utf-8")
        print(f"[blue]Server: {final_response}[/blue]")

        if final_response == "Successfully updated user credentials!":
            set_username(new_username)
            print(f"New Username: [green]{new_username}[/green]")

    except socket.timeout:
        print("[red]Error: The server is taking too long to respond.[/red]")
    except socket.error as e:
        print(f"[red]Socket error occurred: {e}[/red]")
    except Exception as e:
        print(f"[red]An unexpected error occurred: {e}[/red]")

    finally:
        # Reset timeout to default (blocking) for other functions if necessary
        s.settimeout(None)


def register_user(s: socket.socket):
    try:
        s.settimeout(10.0)

        # Send Registration Request Message
        s.sendall(f"reg#{get_username()}#".encode())
        server_message = s.recv(1024).decode("utf-8")
        print(f"[blue]Server: {server_message}[/blue]")

        username = input("Enter a username: ")
        password = input("Enter a password: ")

        registration_message = f"{username}#{password}"

        s.sendall(registration_message.encode("utf-8"))
        final_response = s.recv(1024).decode("utf-8")

        print(f"[blue]Server: {final_response}[/blue]")

        if final_response == "Successfully Registered User!":
            set_username(username)
            print(f"Registered User: [green]{username}[/green]")

    except socket.timeout:
        print("[red]Error: The server is taking too long to respond.[/red]")
    except socket.error as e:
        print(f"[red]Socket error occurred: {e}[/red]")
    except Exception as e:
        print(f"[red]An unexpected error occurred: {e}[/red]")

    finally:
        # Reset timeout to default (blocking) for other functions if necessary
        s.settimeout(None)


if __name__ == "__main__":
    talk_to_server(attempt_connect(get_host(), int(get_port())))
