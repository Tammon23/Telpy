import threading
import socket

from ReceiveableData import ReceiveableData
from SendableData import Profile, Text, ServerCommand, SendableData
from constants import MAX_BYTE_TRANSFER


class Client(ReceiveableData):
    def __init__(self, username: str, host: str = None, port: int = None, client: socket.socket = None):
        self.username = username
        self.profile = Profile(username)
        if client is None:
            if host is None or port is None:
                raise ValueError("Either provide a client or a host and port")
            else:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client.connect((host, port))

        else:
            self.client = client

    def start(self):
        read_packet_thread = threading.Thread(target=self.read_packet)
        read_packet_thread.start()

        send_packet_thread = threading.Thread(target=self.send_packet)
        send_packet_thread.start()

    def send(self, message: SendableData):
        for data in message.get_as_bytes():
            self.client.send(data)

    def close(self):
        self.client.close()

    def read_packet(self):
        client = self.client
        while True:
            try:
                message_length = client.recv(4)
                buffer = [client.recv(MAX_BYTE_TRANSFER) for _ in range(int.from_bytes(message_length, byteorder='big'))]
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

            except Exception as e:
                print(f"An error occurred ==> {e}")
                self.client.close()
                break

    def send_packet(self):
        while True:
            message = input()

            if message == 'quit':
                self.close()
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
