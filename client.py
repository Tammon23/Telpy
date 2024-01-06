import socket
import threading


class Client:
    def __init__(self, username: str, host: str = None, port: int = None, client: socket.socket = None):
        self.username = username

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

    def send(self, message):
        self.client.send(message)

    def close(self):
        self.client.close()

    def read_packet(self):
        client = self.client
        while True:
            try:
                message = client.recv(1024).decode("ascii")
                if message == "getName":
                    client.send(self.username.encode("ascii"))
                else:
                    print(message)

            except Exception as e:
                print(f"An error occurred ==> {e}")
                self.client.close()
                break

    def send_packet(self):
        while True:
            message = f"{self.username}: {input("")}"
            self.client.send(message.encode("ascii"))


if __name__ == "__main__":
    name = input("Enter your username: ")
    client = Client(username=name, host="127.0.0.1", port=65432)
    client.start()
