import socket


class ServerDeputy:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host: str, port: int):
        self.server.bind((host, port))
        self.server.listen(5)
        while True:
            client, addr = self.server.accept()
            print(f"Client {addr} connected")
            client.sendall(b"Hello, world!")
            client.close()
