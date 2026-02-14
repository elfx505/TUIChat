import sqlite3
import bcrypt
import os
import socket
from pathlib import Path
from threading import Thread
from server_db_config import (
    create_db,
    update_user,
    add_message,
    add_user,
    get_user,
    register_user,
    save_message,
)

HOST = "0.0.0.0"
PORT = 7632
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE_PATH = Path(BASE_DIR) / "server_db.json"
MAX_CONNECTIONS = 5

connected_users = []


def listen(server_socket):
    while True:
        client_socket, address = server_socket.accept()
        print(f"[CONNECTED] {address} connected.")

        auth_message = client_socket.recv(1024).decode("utf-8")

        username, password = auth_message.split("#")

        # Hash Password with bcrypt
        salt = bcrypt.gensalt()
        hash_pass = bcrypt.hashpw(password, salt)

        # Check if username is already in the server db
        user_data = get_user(username)
        if user_data:
            # Check Hash to confirm identity
            is_authentic: bool = bcrypt.checkpw(user_data["password"], hash_pass)

        if not is_authentic:
            client_socket.send("Authentication failed!".encode("utf-8"))
            client_socket.close()
            continue

        # If the username does not exist
        if not user_data:
            register_user(username, hash_pass)

        # Add new client object to connected_users list
        client = get_user(username)
        connected_users.append(client)
        print(connected_users)

        broadcast_message(
            username, client["user_uuid"], "", " has joined the chat!"
        )  # Entered the chat message

        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):

    username = client["username"]
    user_id = client["user_uuid"]
    client_socket = client["client_socket"]

    while True:

        # Listen for message from client
        data = client_socket.recv(1024)
        message_content = data.decode("utf-8")

        if message_content.strip() == "/exit" or not message_content.strip():
            broadcast_message(
                username, user_id, "", " has left the chat!"
            )  # Left The Chat Message

            connected_users.remove(client)
            client_socket.close()
            break
        else:
            broadcast_message(
                username, user_id, message_content
            )  # Broadcast actual message across channel clients

        # Append message to db
        save_message(user_id, message_content)


def broadcast_message(
    username: str, uuid: str, message_content: str, override_message=None
):

    message = f"{username}: {message_content}"

    if override_message:
        message = username + str(override_message)

    for client in connected_users:
        client_socket = client["client_socket"]
        client_user_id = client["user_uuid"]
        if client_user_id != uuid:
            client_socket.send(message.encode())


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_CONNECTIONS)
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    # Create DB if it does not exist already
    create_db()

    # Start accepting client connections
    listen(server_socket)


if __name__ == "__main__":
    start_server()
