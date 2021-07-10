import logging, selectors
from socketserver import StreamRequestHandler

class BaseProxy(StreamRequestHandler):
    def exit(self, reason):
        self.server.close_request(self.request)
        raise Exception(reason)

    def forward(self, sock_a, sock_b, size = 4096):
        chunk = sock_a.recv(size)
        if not chunk:
            self.exit('EOF')
        sock_b.send(chunk)

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
        except Exception as e:
            logging.error(e)
            # traceback.print_exc()
            fds = [*selector.get_map()]
            for fd in fds:
                selector.unregister(fd)
            self.server.close_request(self.request)
            self.remote.close()
            
