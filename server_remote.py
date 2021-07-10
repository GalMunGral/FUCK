import logging, selectors, socket, traceback
from socketserver import ThreadingTCPServer, StreamRequestHandler
from simple_http import recv_http_message, make_response, make_empty_response

logging.basicConfig(level=logging.DEBUG)
SOCKS_VERSION = 5
NO_AUTHENTICATION_REQUIRED = 0
IPV4 = 1
IPV6 = 4
DOMAINNAME = 3
CONNECT = 1
SUCCESS = 0
CONNECTION_REFUSED = 5

def forward(sock_a, sock_b, size = 4096):
    sock_b.send(sock_a.recv(size))

class RemoteProxy(StreamRequestHandler):
    def fail(self, reason):
        self.server.close_request(self.request)
        raise Exception(reason)

    def accept(self):
        req = recv_http_message(self.connection)
        if not req:
            res = make_empty_response()
            self.connection.sendall(res.encode())
            self.fail('invalid request')
        logging.info(f"accepted: {self.client_address[0]} {self.client_address[1]}")
        return req

    def connect(self, req):
        addr_type = req['Type']
        port = req['X-TOKEN-P']

        if addr_type == 'V4':
            address = req['X-TOKEN-A']
        elif addr_type == 'DN':
            domain_name = req['X-TOKEN-A']
            address = socket.gethostbyname(domain_name)
            logging.info(f"{domain_name} ~ {address}")

        try:
            self.remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.remote.connect((address, port))
            bnd_addr, bnd_port = self.remote.getsockname()
            logging.info(f"{bnd_addr}:{bnd_port} <--> {address}:{port}")
            res = make_response(bnd_addr, bnd_port)
            self.connection.sendall(res.encode())
            
        except Exception as e:
            traceback.print_exc()
            res = make_empty_response()
            self.connection.sendall(res.encode())
            self.fail('failed to connect')

    def handle(self):
        selector = selectors.DefaultSelector()
        try: 
            self.connect(self.accept())
            selector.register(self.connection, selectors.EVENT_READ, self.remote)
            selector.register(self.remote, selectors.EVENT_READ, self.connection)

            while True:
               for key, _ in selector.select():
                   forward(key.fileobj, key.data)
        except:
            traceback.print_exc()
            fds = [*selector.get_map()]
            for fd in fds:
                selector.unregister(fd)

    
if __name__ == "__main__":
    with ThreadingTCPServer(("0.0.0.0", 443), RemoteProxy) as server:
        server.serve_forever()
