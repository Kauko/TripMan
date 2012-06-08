import time
import random
import socket
from select import select
from messages import get_unpacker, pack_cid, pack_server_full

class Server:
    def __init__(self, address):
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(0)
        self.socket.bind(self.address)
        self.running = False
        self.sockets = dict()

    def descriptors(self):
        yield self.socket

        for descriptor in self.sockets:
            yield descriptor

    def generate_id(self):
        cid = chr(random.randint(65,90))
        while cid in self.sockets.values():
            cid = chr(random.randint(65,90))
        return cid

    def run(self):
        if self.running:
            return

        self.socket.listen(4)
        self.running = True
        while self.running:
            r, w, x = select(self.descriptors(), [], [], 1/20.0)

            for descriptor in r:
                if descriptor == self.socket:
                    descriptor, address = self.socket.accept()
                    if len(self.sockets) > 3:
                        descriptor.send(pack_server_full())
                        descriptor.close()
                        continue

                    cid = self.generate_id()
                    print "%s: connected" % cid
                    self.sockets[descriptor] = cid
                    descriptor.send(pack_cid(cid))
                elif descriptor in self.sockets:
                    cid = self.sockets[descriptor]

                    data = None
                    try:
                        mid = descriptor.recv(1)
                        if mid:
                            length, unpacker = get_unpacker(mid)
                            if length:
                                data = mid + descriptor.recv(length)
                    except socket.error, err:
                        print "socket.error", repr(err)

                    if not data:
                        print "%s: disconnected" % cid
                        del self.sockets[descriptor]
                    else:
                        for descriptor in self.sockets:
                            try:
                                start = time.time()
                                descriptor.send(data)
                            except socket.error, err:
                                print "socket.error", repr(err)
                                del self.sockets[descriptor]

if __name__ == "__main__":
    s = Server(("", 6660))
    s.run()
