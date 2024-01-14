import threading
import socket

from ReceiveableData import ReceiveableData
from SendableData import Profile, Text, ServerCommand, SendableData
from constants import MAX_BYTE_TRANSFER


class Client(ReceiveableData):
    def __init__(self, username: str, host: str = None, port: int = None, client: socket.socket = None):
        self.username = username
        self.profile = Profile(username)
        self.active_threads: list[threading.Thread] = []
        if client is None:
            if host is None or port is None:
                raise ValueError("Either provide a client or a host and port")
            else:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client.connect((host, port))

        else:
            self.client = client

        self.CONNECTED_TO_SERVER = True

    def start(self):
        read_packet_thread = threading.Thread(target=self.read_packet)
        read_packet_thread.start()

        send_packet_thread = threading.Thread(target=self.send_packet, daemon=True)
        send_packet_thread.start()

        self.active_threads = [read_packet_thread, send_packet_thread]

    def send(self, message: SendableData):
        for data in message.get_as_bytes():
            self.client.send(data)

    def close(self):
        self.client.shutdown(socket.SHUT_RDWR)

    def read_packet(self):
        client = self.client
        while self.CONNECTED_TO_SERVER:
            try:
                message_length = int.from_bytes(client.recv(4), byteorder='big')
                buffer = []
                while message_length != 0:
                    read = min(message_length, MAX_BYTE_TRANSFER)
                    buffer.append(client.recv(read))
                    message_length -= read

                obj = self.get_from_bytes(buffer)
                if isinstance(obj, Profile):
                    self.send(self.profile)
                elif isinstance(obj, Text):
                    if obj.source is None:
                        print(f"Unknown: {obj.data}")
                    else:
                        print(f"{obj.source.name}: {obj.data}")

                else:
                    print("ERROR")

            except EOFError:
                print("Successfully disconnected.")
                self.CONNECTED_TO_SERVER = False
                self.close()
                break
            except ZeroDivisionError as e:
                print(f"An error occurred ==> {e}")
                self.close()
                break

    def send_packet(self):
        while self.CONNECTED_TO_SERVER:
            message = input("> ")

            if message == 'quit':
                self.close()
                self.CONNECTED_TO_SERVER = False
                break

            # if input is a command
            if message.startswith(ServerCommand.pattern):
                command = message[1:].split(" ")
                payload = ServerCommand(
                    command[0],
                    command[1:]
                )
            # if the input is regular text
            else:
                payload = Text(message)

            self.send(payload)


if __name__ == "__main__":
    name = input("Enter your username: ")
    client = Client(username=name, host="127.0.0.1", port=65432)
    client.start()
