import logging, socket, struct, argparse 
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

parser = argparse.ArgumentParser()
parser.add_argument("--host", dest="remote_ip", default="127.0.0.1")
parser.add_argument("--port", dest="remote_port", default=2080, type=int)
config = parser.parse_args()


class LocalProxy(BaseProxy, StreamRequestHandler):
    def accept(self):
        logging.info(f"Accepting: {self.client_address}")
        version, nmethods = struct.unpack("!BB", self.connection.recv(2))
        methods = [ord(self.connection.recv(1)) for _ in range(nmethods)]
        assert version == SOCKS_VERSION and NO_AUTHENTICATION_REQUIRED in methods

        # connect to remote
        self.remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.remote.connect((config.remote_ip, config.remote_port))
        self.remote.sendall("fuck".encode("utf-8"))

        if ord(self.remote.recv(1)) != 0:
            self.exit("Handshake failed")
        self.connection.sendall(struct.pack("!BB", SOCKS_VERSION, 0))

    def connect(self):
        version, cmd, _ = struct.unpack("!BBB", self.connection.recv(3))
        assert version == SOCKS_VERSION and cmd == CONNECT

        # forward address type
        addr_type = ord(self.connection.recv(1))
        self.remote.sendall(bytes([addr_type]))

        # forward IP address / domain name
        if addr_type == IPV4:
            self.remote.sendall(self.connection.recv(4))
        elif addr_type == DOMAINNAME:
            domain_length = ord(self.connection.recv(1))
            self.remote.sendall(bytes([domain_length]))
            self.remote.sendall(self.connection.recv(domain_length))

        # forward port
        self.remote.sendall(self.connection.recv(2))

        if ord(self.remote.recv(1)) != 0:
            res = struct.pack(
                "!BBBBIH", SOCKS_VERSION, CONNECTION_REFUSED, 0, addr_type, 0, 0
            )
            self.connection.sendall(res)
            self.exit("[REMOTE] Failed to connect")
        bnd_addr, bnd_port = struct.unpack("!IH", self.remote.recv(6))
        logging.info(f"[REMOTE] Connected")
        res = struct.pack(
            "!BBBBIH", SOCKS_VERSION, SUCCESS, 0, IPV4, bnd_addr, bnd_port
        )
        self.connection.sendall(res)

if __name__ == "__main__":
    with ThreadingTCPServer(("127.0.0.1", 1080), LocalProxy) as server:
        server.serve_forever()
