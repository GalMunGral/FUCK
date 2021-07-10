import logging, selectors
from socket import socket
from socketserver import StreamRequestHandler

class Fuck(StreamRequestHandler):
    def accept():
        pass

    def connect() -> socket:
        pass

    def forward(self, sock_a: socket, sock_b: socket, size: int = 4096) -> bool:
        chunk = sock_a.recv(size)
        if not chunk: 
            return True
        sock_b.send(chunk)
        return False

    def event_loop(self, sock_a: socket, sock_b: socket):
        selector = selectors.DefaultSelector()
        selector.register(sock_a, selectors.EVENT_READ, sock_b)
        selector.register(sock_b, selectors.EVENT_READ, sock_a)
        EOF = False
        while not EOF:
            for key, _ in selector.select():
                try:
                    EOF = self.forward(key.fileobj, key.data) 
                except Exception as e:
                    logging.error(e)
                    break
        selector.unregister(sock_a)
        selector.unregister(sock_b)

    def handle(self):
        try:
            self.accept()
            self.event_loop(self.connection, self.connect())
        except Exception as e:
            logging.error(e) 
