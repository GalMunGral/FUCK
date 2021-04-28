import logging
import select
import socket
import struct
from socketserver import ThreadingTCPServer, StreamRequestHandler
import traceback

logging.basicConfig(level=logging.DEBUG)
SOCKS_VERSION = 5
NO_AUTHENTICATION_REQUIRED = 0
IPV4 = 1
IPV6 = 4
DOMAINNAME = 3
CONNECT = 1
SUCCESS = 0
CONNECTION_REFUSED = 5

class SocksProxy(StreamRequestHandler):
    def handle(self):
        ip, port = self.client_address
        logging.info(f'Accepting connection from {ip}:{port}')

	    # greeting
        hello = self.connection.recv(8).decode('utf-8')
        assert hello == 'fuck-gfw'
        self.connection.sendall(struct.pack("!B", 0))

        # try connecting to remote
        address_type = ord(self.connection.recv(1))
        if address_type == IPV4:
            address = socket.inet_ntoa(self.connection.recv(4))
        elif address_type == DOMAINNAME:
            domain_length = ord(self.connection.recv(1))
            domain_name = self.connection.recv(domain_length).decode('utf-8')
            address = socket.gethostbyname(domain_name)
            logging.info(f'Resolved {domain_name} to {address}')
        port, = struct.unpack('!H', self.connection.recv(2))

        try:
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.connect((address, port))
            logging.info(f'Connected to {address}:{port}')
            bound_addr, bound_port = remote.getsockname()
            bound_addr, = struct.unpack('!I', socket.inet_aton(bound_addr))
            # success
            reply = struct.pack("!BIH", 0, bound_addr, bound_port)

        except Exception as err:
            traceback.print_stack()
            # failure
            reply = struct.pack("!BIH", 1, 0, 0)

        self.connection.sendall(reply)

        # connection established
        if reply[0] == 0:
            self.loop(self.connection, remote)
        self.server.close_request(self.request)


    def loop(self, client, remote):
        while True:
            r, _, _ = select.select([client, remote], [], [])

            if client in r:
                data = client.recv(4096)
                if remote.send(data) <= 0:
                    break

            if remote in r:
                data = remote.recv(4096)
                if client.send(data) <= 0:
                    break

if __name__ == '__main__':
    with ThreadingTCPServer(('127.0.0.1', 2080), SocksProxy) as server:
        server.serve_forever()
