import json
import os
import socket
from pathlib import Path
from threading import Thread

HOST = "127.0.0.1"
PORT = 7632
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE_PATH = Path(BASE_DIR) / "server_db.json"
MAX_CONNECTIONS = 10

connected_users = []


def send_message(sock, message_dict):
    print(message_dict)
    data = json.dumps(message_dict).encode("utf-8")
    sock.send(data)


def append_message_to_db(message_dict):
    message_to_append = {
        "uuid": message_dict["uuid"],
        "username": message_dict["username"],
        "message_content": message_dict["message_content"],
    }

    # Load DB
    db = json.loads(DB_FILE_PATH.read_text())

    # Edit db in memory
    db["messages"].append(message_to_append)

    # Update db in persistent memory
    DB_FILE_PATH.write_text(json.dumps(db, indent=2))


def listen(server_socket):
    while True:
        client_socket, address = server_socket.accept()
        print(f"[CONNECTED] {address} connected.")

        message_dict = json.loads(client_socket.recv(1024).decode("utf-8"))

        username = message_dict.get("username")
        user_id = message_dict.get("uuid")
        # First message will be the /register message
        if user_id == "u_":
            user_id = generate_uuid()
            # Send message containing Identity (UUID) to user
            client_socket.send(str(user_id).encode())

            # Load DB
            db = json.loads(DB_FILE_PATH.read_text())

            # Edit db in memory
            db["users"][user_id] = username

            # Update db in persistent memory
            DB_FILE_PATH.write_text(json.dumps(db, indent=2))

        # Create new client object
        client = {
            "username": username,
            "uuid": user_id,
            "client_socket": client_socket,
        }

        # Add new client object to connected_users list
        connected_users.append(client)
        print(connected_users)

        broadcast_message(
            username, user_id, "", " has joined the chat!"
        )  # Entered the chat message

        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):

    username = client["username"]
    user_id = client["uuid"]
    client_socket = client["client_socket"]

    while True:

        # Listen for message from client
        data = client_socket.recv(1024)
        message_dict = json.loads(data.decode("utf-8"))
        message_content = message_dict.get("message_content")

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
        append_message_to_db(message_dict)


def broadcast_message(
    username: str, uuid: str, message_content: str, override_message=None
):

    message = f"{username} ({uuid}): {message_content}"

    if override_message:
        message = username + str(override_message)

    for client in connected_users:
        client_socket = client["client_socket"]
        client_user_id = client["uuid"]
        if client_user_id != uuid:
            client_socket.send(message.encode())


def generate_uuid() -> str:
    db = json.loads(DB_FILE_PATH.read_text())
    next_uuid = len(db["users"])
    return f"u{str(next_uuid)}"


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_CONNECTIONS)
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    # Start accepting client connections
    listen(server_socket)


if __name__ == "__main__":
    start_server()
