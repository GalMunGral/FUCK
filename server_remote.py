import logging
import select
import socket
import struct
from socketserver import ThreadingTCPServer, StreamRequestHandler
import traceback
from relay import RelayMixin
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


class RemoteProxy(RelayMixin, StreamRequestHandler):
    def fail(self, reason):
        self.server.close_request(self.request)
        raise Exception(reason)

    def connect(self):
        logging.info(f"Accepting connection from {self.client_address}")
        
        req = recv_http_message(self.connection)
        if not req:
            res = make_empty_response()
            self.connection.sendall(res.encode())
            self.fail('Invalid request')
            return

        addr_type = req['Type']
        port = req['X-TOKEN-P']

        if addr_type == 'V4':
            address = req['X-TOKEN-A']
        elif addr_type == 'DN':
            domain_name = req['X-TOKEN-A']
            address = socket.gethostbyname(domain_name)
            logging.info(f"Resolved {domain_name} to {address}")

        try:
            self.remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.remote.connect((address, port))
            bnd_addr, bnd_port = self.remote.getsockname()
            logging.info(f"Connected to {address}:{port} -> {bnd_addr}:{bnd_port}")

            res = make_response(bnd_addr, bnd_port)
            self.connection.sendall(res.encode())
        except Exception as e:
            # logging.error(e)
            traceback.print_exc()
            res = make_empty_response()
            self.connection.sendall(res.encode())
            self.fail('Failed to connect to server')

    def handle(self):
        try:
            self.connect()
            self.run_select(self.connection, self.remote)
            # self.run_poll(self.connection, self.remote)
        except Exception as e:
            # logging.error(e)
            traceback.print_exc()
        self.server.close_request(self.request)


if __name__ == "__main__":
    with ThreadingTCPServer(("0.0.0.0", 9090), RemoteProxy) as server:
        server.serve_forever()
