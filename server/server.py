import bcrypt
import os
import socket
from pathlib import Path
from threading import Thread
from server_db_config import (
    create_db,
    update_user,
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

        try:
            initial_message = client_socket.recv(1024).decode("utf-8")
            if not initial_message:
                continue

            # This allows the password itself to contain # symbols safely.
            parts = initial_message.split("#", 2)
            if len(parts) < 3:
                client_socket.sendall("Invalid protocol format.".encode())
                client_socket.close()
                continue

            request_type, username, password = parts

            # Turn password into an array of bytes
            password_bytes = password.encode("utf-8")

            # Check if username is already in the server db
            user_data = get_user(username)

            is_authentic: bool = False

            if user_data:
                # Ensure Bytes before checking
                stored_hash = user_data["password_hash"]
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode("utf-8")

                # Check Hash to confirm identity
                is_authentic = bcrypt.checkpw(password_bytes, stored_hash)

                if not is_authentic:
                    client_socket.sendall("Authentication failed!".encode("utf-8"))
                    client_socket.close()
                    continue

            # --- CHUSER LOGIC ---
            if request_type == "chuser" and not user_data:
                client_socket.sendall(
                    f"User [{username}] does not exist!".encode("utf-8")
                )
                client_socket.close()
                continue

            if request_type == "chuser" and is_authentic:
                client_socket.sendall("AUTH_SUCCESS".encode("utf-8"))
                new_credentials_message = client_socket.recv(1024).decode("utf-8")
                new_username, new_password = new_credentials_message.split("#", 1)

                if get_user(new_username) and username != new_username:
                    client_socket.sendall("Username already in use!".encode("utf-8"))
                    client_socket.close()
                    continue

                # Hash and convert to string for consistent DB storage
                new_hash = bcrypt.hashpw(
                    new_password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")

                if update_user(new_username, new_hash, user_data["user_uuid"]):
                    client_socket.sendall(
                        f"Successfully updated user credentials!".encode("utf-8")
                    )

                client_socket.close()
                continue

            # --- AUTH / REGISTRATION LOGIC ---

            # If the username does not exist
            if request_type == "auth" and not user_data:
                # Hash
                hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")
                register_user(username, hashed)

            # Add new client object to connected_users list
            client = get_user(username)
            client["client_socket"] = client_socket

            connected_users.append(client)
            print(connected_users)

            client_socket.sendall("Successful Authentication!".encode("utf-8"))

            broadcast_message(
                username, client["user_uuid"], "", " has joined the chat!"
            )  # Entered the chat message

            Thread(target=handle_client, args=(client,)).start()

        except Exception as e:
            print(f"[ERROR] Error during initial handshake: {e}")
            client_socket.close()


def handle_client(client):
    username = client["username"]
    user_id = client["user_uuid"]
    client_socket = client["client_socket"]

    try:
        while True:
            # Receive data
            data = client_socket.recv(1024)

            # Check for empty data
            if not data:
                break

            message_content = data.decode("utf-8").strip()

            # Handle explicit exit command
            if message_content == "/exit":
                break

            # Handle actual messages
            if message_content:
                broadcast_message(username, user_id, message_content)
                save_message(user_id, message_content)

    except (ConnectionResetError, BrokenPipeError):
        print(f"[DISCONNECT] {username} lost connection abruptly.")
    except Exception as e:
        print(f"[ERROR] {username} thread encountered error: {e}")
    finally:
        # Guaranteed Cleanup
        if client in connected_users:
            connected_users.remove(client)

        client_socket.close()
        broadcast_message(username, user_id, "", " has left the chat!")
        print(f"[INFO] {username} has been cleaned up.")


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
            client_socket.sendall(message.encode())


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
