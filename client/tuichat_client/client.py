import os
import socket
from threading import Thread

from user_config import get_host, get_port, get_username


def attempt_connect(socket: socket.socket, host: str, port: int) -> None:
    if not host or not port:
        print("""
        Missing server hostname and/or server port number information!
        Set values with 'tchat host <address> <port_number>'
        """)

        os._exit(
            0
        )  # Needs to provide server address before proceeding. Exit early if they are missing

    try:
        socket.connect((host, port))

    except ConnectionRefusedError as e:
        print(f"Server at {host}:{port} does not exist or is currently offline!")
        os._exit(0)  # Invalid host and/or port. Exit early


def receive_message():
    while True:
        server_message = s.recv(1024).decode()
        if not server_message.strip():
            print("\033[1;31;40mConnection to server closed!\033[0m")
            os._exit(0)

        print("\033[1;31;40m" + str(server_message) + "\033[0m")


def send_message():
    while True:
        client_input = input("")
        s.send(client_input.encode())


def talk_to_server():

    password = input("Enter your Password: ")

    # Send Register Message and await response from server
    s.send(f"{get_username()}#{password}".encode())

    Thread(target=receive_message, daemon=True).start()
    send_message()


if __name__ == "__main__":
    s = socket.socket()
    attempt_connect(s, get_host(), int(get_port()))
    talk_to_server()
