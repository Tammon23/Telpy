import socket
import threading

from ReceiveableData import ReceiveableData
from SendableData import Text, Profile, SendableData
from client import Client
from constants import MAX_BYTE_TRANSFER


class Server(ReceiveableData):
    def __init__(self, host: str, port: int, name: str = None) -> None:
        self.host = host
        self.port = port
        self.name: str | None = name
        self.profile = Profile("SERVER")

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected_clients: dict[tuple[str, int], Client] = {}

    def start(self) -> None:
        HOST = self.host
        PORT = self.port
        SERVER = self.server

        SERVER.bind((HOST, PORT))
        SERVER.listen()
        print(f"Server started listening on {HOST}:{PORT}")
        self.listen_for_connections()

    def send(self, message: SendableData, client: Client | socket.socket) -> None:
        if isinstance(client, Client):
            for data in message.get_as_bytes():
                client.client.send(data)
        else:
            for data in message.get_as_bytes():
                client.send(data)

    def terminate_connection(self, client_id: tuple[str, int], termination_message: str = None) -> None:
        client = self.connected_clients.pop(client_id)
        self.broadcast_message(Text(f"{client.username} has disconnected!", source=self.profile))
        if termination_message is not None:
            print(termination_message)

        client.close()

    """ 
    listens for new connections to the server, when a connection is established
    server asks the client for its name, saves the client, and starts a new thread
    used for listening for new messages from said client
    """

    def listen_for_connections(self):
        while True:
            # accept connection from new client
            client, address = self.server.accept()  # address: host addr, port
            print(f"New connection from {address}")

            # ask client for a name
            self.send(Profile(), client)
            message_length = int.from_bytes(client.recv(4), byteorder='big')

            buffer = []
            while message_length != 0:
                read = min(message_length, MAX_BYTE_TRANSFER)
                buffer.append(client.recv(read))
                message_length -= read
            obj = self.get_from_bytes(buffer)

            if obj is None or not isinstance(obj, Profile):
                print("uh oh")
                continue

            # grab the nickname from the users profile obj and save the client
            nickname = obj.name
            self.connected_clients[address] = Client(nickname, client=client)

            print(f"New client connected: {nickname}")
            self.broadcast_message(Text(f"New client connected: {nickname}", source=self.profile), nickname)

            # telling the connected client that they connected safely
            self.send(Text("Successfully connected to the server!", source=self.profile), client)

            # starting thread to monitor all incoming messages
            thread = threading.Thread(target=self.receive_message, args=(client,))
            thread.start()

    def broadcast_message(self, message: SendableData, excluding: str | None = None) -> None:
        message_bytes = list(message.get_as_bytes())
        for connected_client in self.connected_clients.values():
            if excluding is None or connected_client.username != excluding:
                for data in message_bytes:
                    connected_client.client.send(data)

    def receive_message(self, client: socket.socket) -> None:
        while True:
            try:
                # get the message object
                message_length = int.from_bytes(client.recv(4), byteorder='big')

                buffer = []
                while message_length != 0:
                    read = min(message_length, MAX_BYTE_TRANSFER)
                    buffer.append(client.recv(read))
                    message_length -= read
                obj = self.get_from_bytes(buffer)

                # if the user wants to quit the session, terminate their connection
                if isinstance(obj, Text) and obj.data == "quit":
                    self.terminate_connection(client.getsockname()[1])

                # otherwise relay their message to everyone else
                else:
                    obj.source = self.connected_clients[client.getpeername()].profile
                    self.broadcast_message(obj)

            except Exception as e:
                print("An error occurred:", e)
                self.terminate_connection(client.getpeername(), "An error occurred in your connection")
                break


if __name__ == "__main__":
    server = Server(host="127.0.0.1", port=65432)
    server.start()
