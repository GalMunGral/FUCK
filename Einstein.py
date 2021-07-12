import logging
import socket
import argparse
import struct
from Schwarzschild import Schwarzschild
from socketserver import ThreadingTCPServer

logging.basicConfig(level=logging.DEBUG)
IPV4 = 1
IPV6 = 4
DOMAIN_NAME = 3
SUCCESS = 0
CONN_REFUSED = 5

parser = argparse.ArgumentParser()
parser.add_argument("--listen", dest="einstein_port", default=443, type=int)
config = parser.parse_args()

class Einstein(Schwarzschild):
    def handshake_ok(self):
        self.connection.sendall(b"\x00")

    def accept(self):
        name = self.connection.recv(9)
        if name != b"Minkowski":
            logging.error(f"[{name}] called but I don't feel like answering")
            raise Exception("[EINSTEIN] I'm not ok")
        self.handshake_ok()
        logging.info(f"Accepted {self.client_address}")

    def ok(self, bnd_addr: str, bnd_port: int):
        (bnd_addr,) = struct.unpack("!I", socket.inet_aton(bnd_addr))
        self.connection.sendall(struct.pack(
            "!BIH", SUCCESS, bnd_addr, bnd_port))

    def error(self):
        self.connection.sendall(struct.pack("!BIH", CONN_REFUSED, 0, 0))

    def connect(self):
        addr_type = ord(self.connection.recv(1))
        if addr_type == IPV4:
            address = socket.inet_ntoa(self.connection.recv(4))
        if addr_type == IPV6:
            address = socket.inet_ntoa(self.connection.recv(16))
        elif addr_type == DOMAIN_NAME:
            n_domain_name = ord(self.connection.recv(1))
            domain_name = self.connection.recv(n_domain_name)
            address = socket.gethostbyname(domain_name)
            logging.info(f"{domain_name} ~ {address}")
        (port,) = struct.unpack("!H", self.connection.recv(2))

        try:
            dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dest.connect((address, port))
            bnd_addr, bnd_port = dest.getsockname()
            self.ok(bnd_addr, bnd_port)
            logging.info(
                f"{bnd_addr}:{bnd_port} <--> {address}:{port}")
        except Exception as e:
            logging.error(e)
            self.error()
            raise Exception("[EINSTEIN] I'm not ok")

        return dest


if __name__ == "__main__":
    with ThreadingTCPServer(("0.0.0.0", config.einstein_port), Einstein) as server:
        server.serve_forever()
