import asyncio
import sys

from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Header, Input, Static


class Message(Static):
    """A custom widget for a message bubble."""

    def __init__(self, text: str, sender: str, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.sender = sender

    def compose(self) -> ComposeResult:
        yield Static(f"{self.sender}:", classes="sender-name")
        yield Static(self.text, classes="message-text")


class TUIChat(App):
    BINDINGS = [("ctrl+q", "quit", "Quit")]
    CSS_PATH = "chat.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(id="chat-log")
        yield Input(placeholder="Type a message...", id="chat-input")

    def on_mount(self) -> None:
        """Called when the app starts."""
        # Focus input field immediately
        self.query_one("#chat-input").focus()

        # Temp
        # Start the background listener immediately
        self.recv_message_worker()

    def on_unmount(self) -> None:
        """This runs right before the app fully stops."""
        # Perform Socket close here

    @work(exclusive=True, thread=True)
    def recv_message_worker(self) -> None:
        """A long-running worker that listens for server data."""
        # This represents your client.recv() loop
        while True:
            # Example: data = self.client_socket.recv(1024)
            # For now, let's simulate a message arriving every 5 seconds
            import time

            time.sleep(5)

            # Use call_from_thread to update UI safely from a thread
            self.call_from_thread(self.add_message, "Server says hello!", "received")

    @work
    async def send_message_worker(self, message: str) -> None:
        """A worker to send data to the server."""
        # This is where your self.client_socket.send() goes
        # Using 'async' here if your library is async, or drop 'async' for threads
        await asyncio.sleep(0.1)  # Simulate network latency
        print(f"Sent: {message}")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        msg = event.value.strip()
        if msg:
            self.add_message(msg, "sent")
            self.send_message_worker(msg)  # Fire and forget
            event.input.value = ""

    def add_message(self, text: str, type: str) -> None:
        """Helper to append messages to the UI."""
        chat_log = self.query_one("#chat-log")
        # In a real app, you'd use your Message widget here
        chat_log.mount(Static(text, classes=type))
        chat_log.scroll_end(animate=True)

    async def action_quit(self):
        # Notify your listener worker to stop
        self.workers.cancel_all()

        # Give workers a moment to die, then exit
        self.exit()


if __name__ == "__main__":
    app = TUIChat()
    app.run()
