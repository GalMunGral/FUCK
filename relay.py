import select
import logging

logging.basicConfig(level=logging.DEBUG)


class RelayMixin:
    def run_select(self, sock_a, sock_b):
        socks = [sock_a, sock_b]
        while True:
            fds, _, _ = select.select(socks, [], [])
            i = socks.index(fds[0])
            data = socks[i].recv(4096)
            if socks[i ^ 1].send(data) <= 0:
                self.fail("Errored while sending data")

    def run_poll(self, sock_a, sock_b):
        poll = select.poll()
        socks = [sock_a, sock_b]
        for s in socks:
            poll.register(s, select.POLLIN)
        while True:
            evts = poll.poll()
            if not evts:
                self.fail("Loop timed out")
            fd = evts[0][0]
            for i in [0, 1]:
                if socks[i].fileno() == fd:
                    data = socks[i].recv(4096)
                    if socks[i ^ 1].send(data) <= 0:
                        self.fail("Errored while sending data")
        for s in socks:
            poll.unregister(s)
