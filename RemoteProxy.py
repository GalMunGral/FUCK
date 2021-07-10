import logging, socket, struct
from socketserver import ThreadingTCPServer, StreamRequestHandler
from BaseProxy import BaseProxy

logging.basicConfig(level=logging.DEBUG)
SOCKS_VERSION = 5
NO_AUTHENTICATION_REQUIRED = 0
IPV4 = 1
IPV6 = 4
DOMAINNAME = 3
CONNECT = 1
SUCCESS = 0
CONNECTION_REFUSED = 5


class RemoteProxy(BaseProxy, StreamRequestHandler):
    def accept(self):
        logging.info(f"Accepting: {self.client_address}")
        hello = self.connection.recv(8).decode("utf-8")
        assert hello == "fuck"
        self.connection.sendall(b"\x00")

    def connect(self):
        addr_type = ord(self.connection.recv(1))
        if addr_type == IPV4:
            address = socket.inet_ntoa(self.connection.recv(4))
        elif addr_type == DOMAINNAME:
            domain_length = ord(self.connection.recv(1))
            domain_name = self.connection.recv(domain_length)
            address = socket.gethostbyname(domain_name)
            logging.info(f"{domain_name} ~ {address}")
        (port,) = struct.unpack("!H", self.connection.recv(2))

        try:
            self.remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.remote.connect((address, port))
            bnd_addr, bnd_port = self.remote.getsockname()
            (bnd_addr,) = struct.unpack("!I", socket.inet_aton(bnd_addr))
            logging.info(f"Connected: {bnd_addr}:{bnd_port} <--> {address}:{port}")
            res = struct.pack("!BIH", 0, bnd_addr, bnd_port)
            self.connection.sendall(res)
        except:
            res = struct.pack("!BIH", 1, 0, 0)
            self.connection.sendall(res)

if __name__ == "__main__":
    with ThreadingTCPServer(("0.0.0.0", 9090), RemoteProxy) as server:
        server.serve_forever()
