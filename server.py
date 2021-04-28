import logging
import select
import socket
import struct
from socketserver import ThreadingTCPServer, StreamRequestHandler

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
        version, nmethods = struct.unpack("!BB", self.connection.recv(2))
        methods = [ord(self.connection.recv(1)) for _ in range(nmethods)]
        assert version == SOCKS_VERSION
        assert NO_AUTHENTICATION_REQUIRED in methods
        self.connection.sendall(struct.pack("!BB", SOCKS_VERSION, 0))

        # try connecting to remote
        version, cmd, _, address_type = struct.unpack("!BBBB", self.connection.recv(4))
        assert version == SOCKS_VERSION

        if address_type == IPV4:
            address = socket.inet_ntoa(self.connection.recv(4))
        elif address_type == DOMAINNAME:
            domain_length = ord(self.connection.recv(1))
            domain_name = self.connection.recv(domain_length).decode('utf-8')
            address = socket.gethostbyname(domain_name)
            logging.info(f'Resolved {domain_name} to {address}')
        port = struct.unpack('!H', self.connection.recv(2))[0]

        try:
            if cmd == CONNECT:
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((address, port))
                logging.info(f'Connected to {address}:{port}')
            else:
                logging.error(f'Command {cmd} not implemented!')
                self.server.close_request(self.request)
                return
            bound_addr, bound_port = remote.getsockname()
            bound_addr, = struct.unpack('!I', socket.inet_aton(bound_addr))

            # success
            reply = struct.pack("!BBBBIH", SOCKS_VERSION, SUCCESS, 0, IPV4, bound_addr, bound_port)

        except Exception as err:
            logging.error(err)

            # failure
            reply = struct.pack("!BBBBIH", SOCKS_VERSION, CONNECTION_REFUSED, 0, address_type, 0, 0)

        self.connection.sendall(reply)

        # connection established
        if cmd == CONNECT and reply[1] == SUCCESS:
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
    with ThreadingTCPServer(('127.0.0.1', 1080), SocksProxy) as server:
        server.serve_forever()
