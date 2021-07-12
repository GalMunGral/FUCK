import logging
import socket
import struct
import argparse
from Schwarzschild import Schwarzschild 
from socketserver import ThreadingTCPServer

logging.basicConfig(level=logging.DEBUG)

SOCKS_VER = 5
NO_AUTH_REQUIRED = 0
IPV4 = 1
IPV6 = 4
DOMAIN_NAME = 3
CONNECT = 1
SUCCESS = 0
CONN_REFUSED = 5

parser = argparse.ArgumentParser()
parser.add_argument("--host", dest="einstein_ip", default="127.0.0.1")
parser.add_argument("--port", dest="eintein_port", default=443, type=int)
parser.add_argument("--listen", dest="rosen_port", default=1080, type=int)
parser.add_argument('--verbose', action="store_true")
config = parser.parse_args()


class Rosen(Schwarzschild):
    def setup(self):
        super().setup()
        self.verbose = config.verbose

    def handshake_ok(self):
        self.connection.sendall(struct.pack("!BB", SOCKS_VER, SUCCESS))

    def accept(self):
        version, n_methods = struct.unpack("!BB", self.connection.recv(2))

        if version != SOCKS_VER:
            raise Exception('[SOCK] version not supported')

        methods = []
        for _ in range(n_methods):
            method = ord(self.connection.recv(1))
            methods.append(method)

        if NO_AUTH_REQUIRED not in methods:
            raise Exception('[SOCK] authentication not supported')

        self.handshake_ok()
        logging.info(f"Accepted {self.client_address}")

    def error(self, addr_type: int):
        self.connection.sendall(struct.pack(
            "!BBBBIH", SOCKS_VER, CONN_REFUSED, 0, addr_type, 0, 0))

    def ok(self, bnd_addr: int, bnd_port: int):
        self.connection.sendall(
            struct.pack(
                "!BBBBIH", SOCKS_VER, SUCCESS, 0, IPV4, bnd_addr, bnd_port
            ))

    def connect(self):
        einstein = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        einstein.connect((config.einstein_ip, config.eintein_port))
        einstein.sendall(b"Minkowski")

        not_ok = ord(einstein.recv(1))
        if not_ok:
            raise Exception("[FUCK] that's not ok")

        version, cmd, _ = struct.unpack("!BBB", self.connection.recv(3))

        if version != SOCKS_VER:
            raise Exception('[SOCK] version not supported')
        if cmd != CONNECT:
            raise Exception('[SOCK] command not supported')

        addr_type = self.connection.recv(1)
        einstein.sendall(addr_type)
        addr_type = ord(addr_type)
        if addr_type == IPV4:
            einstein.sendall(self.connection.recv(4))
        if addr_type == IPV6:
            einstein.sendall(self.connection.recv(16))
        elif addr_type == DOMAIN_NAME:
            n_domain_name = self.connection.recv(1)
            einstein.sendall(n_domain_name)
            n_domain_name = ord(n_domain_name)
            einstein.sendall(self.connection.recv(n_domain_name))
        einstein.sendall(self.connection.recv(2))  # port

        not_ok = ord(einstein.recv(1))
        if not_ok:
            self.error(addr_type)
            raise Exception("[FUCK] that's not ok")

        bnd_addr, bnd_port = struct.unpack("!IH", einstein.recv(6))
        self.ok(bnd_addr, bnd_port)
        logging.info(f"Connection Established")

        return einstein


if __name__ == "__main__":
    with ThreadingTCPServer(("127.0.0.1", config.rosen_port), Rosen) as server:
        server.serve_forever()
