import socket
import threading

from client import Client


class Server:
    def __init__(self, host: str, port: int, name: str = None) -> None:
        self.host = host
        self.port = port
        self.name: str | None = name

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected_clients: dict[tuple[str, int], Client] = {}

    def start(self) -> None:
        HOST = self.host
        PORT = self.port
        selfserver = self.server

        selfserver.bind((HOST, PORT))
        selfserver.listen()
        print(f"Server started listening on {HOST}:{PORT}")
        self.add_new_connection()

    def terminate_connection(self, client: tuple[str, int], message: str = None) -> None:
        client = self.connected_clients.pop(client)
        self.broadcast_packet(f"{client.username} has disconnected!".encode("ascii"))
        if message is not None:
            client.send(message)

        client.close()

    def add_new_connection(self):
        while True:
            client, address = self.server.accept()  # address: hostaddr, port
            print(f"New connection from {address} sockname: {client.getsockname()}")

            client.send("getName".encode("ascii"))
            nickname = client.recv(1024).decode("ascii")

            self.connected_clients[address] = Client(nickname, client=client)

            print(f"New client connected: {nickname}")
            self.broadcast_packet(f"New client connected: {nickname}".encode("ascii"))
            client.send("Connected to the server!".encode("ascii"))

            thread = threading.Thread(target=self.handle_connections, args=(client,))
            thread.start()

    def broadcast_packet(self, packet: bytes) -> None:
        for client in self.connected_clients.values():
            client.send(packet)

    def handle_connections(self, client: socket.socket) -> None:
        while True:
            try:
                message = client.recv(1024)
                print(message, message == "quit", message == "quit".encode("ascii"))
                if message == "quit".encode("ascii"):
                    self.terminate_connection(client.getsockname()[1])
                else:
                    self.broadcast_packet(message)

            except Exception as e:
                print("An error occurred:", e)
                self.terminate_connection(client.getsockname()[1], "An error occurred in your connection")
                break


if __name__ == "__main__":
    server = Server(host="127.0.0.1", port=65432)
    server.start()
