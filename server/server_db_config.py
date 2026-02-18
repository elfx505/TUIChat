import sqlite3
from rich.console import Console
from rich.table import Table

sql_statements = [
    # Create User Table
    """
    CREATE TABLE IF NOT EXISTS users (
        user_uuid INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );
    """,
    # Create Messages Table
    # 'user_uuid' here acts as the Foreign Key linking back to the Users table.
    """
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_uuid TEXT,
        message_content TEXT NOT NULL,
        sent_at_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_uuid) REFERENCES users (user_uuid)
    );
    """,
]


def create_db():
    conn = sqlite3.connect("db_server.db")
    try:
        with conn:
            # create a cursor
            cursor = conn.cursor()

            # execute statements
            for statement in sql_statements:
                cursor.execute(statement)

            # commit the changes
            conn.commit()

            print("Tables created successfully.")
    finally:
        conn.close()


def add_user(conn, user):
    # insert table statement
    sql = """ INSERT INTO users(user_uuid,username,password_hash)
              VALUES(?,?,?) """

    # Create  a cursor
    cur = conn.cursor()

    # execute the INSERT statement
    cur.execute(sql, user)

    # commit the changes
    conn.commit()

    # get the id of the last inserted row
    return cur.lastrowid


def add_message(conn, message):
    # insert table statement
    sql = """INSERT INTO messages(message_id,user_uuid,message_content,sent_at_time)
             VALUES(?,?,?,?) """

    # create a cursor
    cur = conn.cursor()

    # execute the INSERT statement
    cur.execute(sql, message)

    # commit the changes
    conn.commit()

    # get the id of the last inserted row
    return cur.lastrowid


def update_user(new_username, new_password, user_id):
    conn = sqlite3.connect("db_server.db", timeout=10)
    sql = "UPDATE users SET username=?, password_hash=? WHERE user_uuid = ?"

    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                sql,
                (
                    new_username,
                    new_password,
                    user_id,
                ),
            )
            conn.commit()
            return True

    except sqlite3.IntegrityError:
        # This triggers if 'username' is already in the table
        print(f"Error: The username '{new_username}' is already taken.")
        return False

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

    finally:
        conn.close()


def get_user(username):
    with sqlite3.connect("db_server.db") as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT * FROM users WHERE username = ?"
        user = conn.execute(query, (username,)).fetchone()

        # Convert to dict
        return dict(user) if user else None


def register_user(username, password_hash):
    conn = sqlite3.connect("db_server.db", timeout=10)

    try:
        with conn:
            query = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            conn.execute(query, (username, password_hash))
            print(f"User '{username}' registered successfully!")
            return True

    except sqlite3.IntegrityError:
        # This triggers if 'username' is already in the table
        print(f"Error: The username '{username}' is already taken.")
        return False

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

    finally:
        conn.close()


def save_message(user_uuid, content):
    # Establish connection with timeout for your 5-thread environment
    conn = sqlite3.connect("db_server.db", timeout=10)
    conn.execute("PRAGMA foreign_keys = ON;")  # Enables the constraint check

    try:
        with conn:
            # We only specify the two columns we are providing
            query = """
                INSERT INTO messages (user_uuid, message_content) 
                VALUES (?, ?)
            """
            conn.execute(query, (user_uuid, content))

    except sqlite3.IntegrityError as e:
        # This triggers if the user_uuid doesn't exist in the users table
        print(f"Foreign Key Error: User ID {user_uuid} is invalid. {e}")
    finally:
        conn.close()


# DEBUG METHODS


def view_all_data():
    """
    Fetches and prints the contents of the 'users' and 'messages' tables.
    """
    console = Console()

    try:
        with sqlite3.connect("db_server.db") as conn:
            conn.row_factory = sqlite3.Row  # Access columns by name
            cursor = conn.cursor()

            # --- DISPLAY USERS TABLE ---
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()

            user_table = Table(
                title="[bold cyan]Users Table[/bold cyan]",
                show_header=True,
                header_style="bold magenta",
            )
            user_table.add_column("UUID", style="dim")
            user_table.add_column("Username")
            user_table.add_column("Password Hash", overflow="fold")

            for user in users:
                # Check if password_hash is bytes; if so, decode it.
                # Otherwise, just use it as is.
                pw_hash = user["password_hash"]
                if isinstance(pw_hash, bytes):
                    pw_hash = pw_hash.decode("utf-8", errors="replace")

                user_table.add_row(
                    str(user["user_uuid"]), str(user["username"]), str(pw_hash)
                )

            console.print(user_table)
            console.print("\n")  # Space between tables

            # --- DISPLAY MESSAGES TABLE ---
            cursor.execute("SELECT * FROM messages")
            messages = cursor.fetchall()

            msg_table = Table(
                title="[bold green]Messages Table[/bold green]",
                show_header=True,
                header_style="bold yellow",
            )
            msg_table.add_column("ID", justify="right")
            msg_table.add_column("User UUID")
            msg_table.add_column("Content")
            msg_table.add_column("Timestamp")

            for msg in messages:
                msg_table.add_row(
                    str(msg["message_id"]),
                    str(msg["user_uuid"]),
                    msg["message_content"],
                    msg["sent_at_time"],
                )

            console.print(msg_table)

    except sqlite3.Error as e:
        console.print(f"[bold red]Database Error:[/bold red] {e}")


if __name__ == "__main__":
    view_all_data()
