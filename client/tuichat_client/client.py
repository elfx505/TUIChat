import os
import socket
from threading import Thread

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
            print("\033[1;31;40mConnection to server closed!\033[0m")
            os._exit(0)

        print("\033[1;31;40m" + str(server_message) + "\033[0m")


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
            print(f"Server denied request: {server_message}")
            return

        print("Authentication successful.")
        new_username = input("Enter your new Username: ")
        new_password = input("Enter your new Password: ")

        # Send the new credentials
        s.sendall(f"{new_username}#{new_password}".encode())

        final_response = s.recv(1024).decode("utf-8")
        print(f"Server: {final_response}")

        if final_response == "Successfully updated user credentials!":
            set_username(new_username)
            print(f"New Username: {new_username}")

    except socket.timeout:
        print("Error: The server is taking too long to respond.")
    except socket.error as e:
        print(f"Socket error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Reset timeout to default (blocking) for other functions if necessary
        s.settimeout(None)


if __name__ == "__main__":
    talk_to_server(attempt_connect(get_host(), int(get_port())))
