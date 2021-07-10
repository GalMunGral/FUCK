import logging, socket, struct, selectors, argparse, traceback
from socketserver import ThreadingTCPServer, StreamRequestHandler
from simple_http import make_request, recv_http_message

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
parser.add_argument("--listen", dest="local_port", default=1080, type=int)
config = parser.parse_args()


class LocalProxy(StreamRequestHandler):
        
    def fail(self, reason):
        self.server.close_request(self.request)
        raise Exception(reason)

    def accept(self):
        version, nmethods = struct.unpack("!BB", self.connection.recv(2))
        methods = [ord(self.connection.recv(1)) for _ in range(nmethods)]

        if version != SOCKS_VERSION:
            self.fail('SOCKS version not supported')
        if NO_AUTHENTICATION_REQUIRED not in methods:
            self.fail('SOCKS auth method not supported')

        self.remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.remote.connect((config.remote_ip, config.remote_port))
        logging.info(f"accepted: {self.client_address[0]} {self.client_address[1]}")
        self.connection.sendall(struct.pack("!BB", SOCKS_VERSION, 0))

    def connect(self):
        version, cmd, _ = struct.unpack("!BBB", self.connection.recv(3))
        if version != SOCKS_VERSION:
            self.fail('SOCKS version not supported')
        if cmd != CONNECT:
            self.fail('SOCKS command not supported')

        addr_type = ord(self.connection.recv(1))
        if addr_type == IPV4:
            address = socket.inet_ntoa(self.connection.recv(4))
            (port,) = struct.unpack("!H", self.connection.recv(2))
            req = make_request('V4', address, port)
            self.remote.sendall(req.encode())
        elif addr_type == DOMAINNAME:
            N = ord(self.connection.recv(1))
            address = self.connection.recv(N).decode()
            (port,) = struct.unpack("!H", self.connection.recv(2))
            req = make_request('DN', address, port)
            self.remote.sendall(req.encode())

        res = recv_http_message(self.remote)

        if not res: 
            res = struct.pack(
                "!BBBBIH", SOCKS_VERSION, CONNECTION_REFUSED, 0, addr_type, 0, 0
            )
            self.connection.sendall(res)
            self.fail("[remote] failed to connect")
            return
    
        logging.info(f"[remote] <--> {address}:{port}")
        bnd_addr = res['X-TOKEN-A']
        bnd_port = res['X-TOKEN-P']
        (bnd_addr_n,) = struct.unpack("!I", socket.inet_aton(bnd_addr))
        res = struct.pack(
            "!BBBBIH", SOCKS_VERSION, SUCCESS, 0, IPV4, bnd_addr_n, bnd_port
        )
        self.connection.sendall(res)
    
    def forward(self, sock_a, sock_b, size = 4096):
        sock_b.send(sock_a.recv(size))

    def handle(self):
        selector = selectors.DefaultSelector()
        try:
            self.accept()
            self.connect()
            selector.register(self.connection, selectors.EVENT_READ, self.remote)
            selector.register(self.remote, selectors.EVENT_READ, self.connection)
            while True:
                for key, _ in selector.select():
                    self.forward(key.fileobj, key.data)
        except:
            traceback.print_exc()
            fds = [*selector.get_map()]
            for fd in fds:
                selector.unregister(fd)

if __name__ == "__main__":
    with ThreadingTCPServer(("127.0.0.1", config.local_port), LocalProxy) as server:
        server.serve_forever()
