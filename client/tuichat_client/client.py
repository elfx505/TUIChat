import json
import os
import socket
from threading import Thread

from user_config import get_host, get_port, load_config, set_uuid


def attempt_connect(socket: socket.socket, host: str, port: int) -> None:
    if not host or not port:
        print(
            """
        Missing server hostname and/or server port number information!
        Set values with 'tchat host <address> <port_number>'
        """
        )

        os._exit(
            0
        )  # Needs to provide server address before proceeding. Exit early if they are missing

    try:
        socket.connect((host, port))

    except ConnectionRefusedError as e:
        print(f"Server at {host}:{port} does not exist or is currently offline!")
        os._exit(0)  # Invalid host and/or port. Exit early


def format_message(content: str) -> str:
    config = load_config()

    # Only keep the fields you want
    allowed_fields = ["uuid", "username"]

    filtered = {
        key: config[key] for key in allowed_fields if key in config
    }  # Create new dict only with alllowed fields from config

    return json.dumps({**filtered, "message_content": content})


def receive_message():
    while True:
        server_message = s.recv(1024).decode()
        if not server_message.strip():
            print("Server is offline!")
            os._exit(0)

        print("\033[1;31;40m" + str(server_message) + "\033[0m")


def send_message():
    while True:
        client_input = input("")
        client_message = format_message(client_input)
        s.send(client_message.encode())


def talk_to_server():
    config = load_config()

    # Send Register Message and await response from server
    s.send(format_message("/register").encode())
    if config["uuid"] == "u_":
        user_id = s.recv(1024).decode()
        print(f"Registered as user '{user_id}'")
        set_uuid(user_id)

    Thread(target=receive_message, daemon=True).start()
    send_message()


if __name__ == "__main__":
    s = socket.socket()
    attempt_connect(s, get_host(), int(get_port()))
    talk_to_server()
