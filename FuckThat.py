import logging
import socket
import struct
import Fuck
from socketserver import ThreadingTCPServer

logging.basicConfig(level=logging.DEBUG)
IPV4 = 1
IPV6 = 4
DOMAIN_NAME = 3
SUCCESS = 0
CONN_REFUSED = 5


class FuckThat(Fuck.Fuck):
    def fuck_handshake_ok(self):
        self.connection.sendall(b"\x00")

    def accept(self):
        the_word = (self.connection.recv(8)).decode()
        if the_word != "fuck":
            logging.error(f'Got the word: {the_word}')
            raise Exception("[FUCK] I'm not ok")
        self.fuck_handshake_ok()
        logging.info(f"Accepted {self.client_address}")

    def fuck_ok(self, bnd_addr: str, bnd_port: int):
        (bnd_addr,) = struct.unpack("!I", socket.inet_aton(bnd_addr))
        self.connection.sendall(struct.pack(
            "!BIH", SUCCESS, bnd_addr, bnd_port))

    def fuck_error(self):
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
            self.fuck_ok(bnd_addr, bnd_port)
            logging.info(
                f"{bnd_addr}:{bnd_port} <--> {address}:{port}")
        except Exception as e:
            logging.error(e)
            self.fuck_error()
            raise Exception("[FUCK] I'm not ok")

        return dest


if __name__ == "__main__":
    with ThreadingTCPServer(("0.0.0.0", 443), FuckThat) as server:
        server.serve_forever()
