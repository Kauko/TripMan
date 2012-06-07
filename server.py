import time
import uuid
import socket
from select import select

class Server:
    def __init__(self, address):
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(0)
        self.socket.bind(self.address)
        self.running = False
        self.sockets = dict()

    def descriptors(self):
        yield self.socket

        for descriptor in self.sockets:
            yield descriptor

    def generate_id(self):
        cid = str(uuid.uuid4())
        while cid in self.sockets.values():
            cid = str(uuid.uuid4())
        return cid

    def run(self):
        if self.running:
            return

        self.socket.listen(4)
        self.running = True
        while self.running:
            r, w, x = select(self.descriptors(), self.descriptors(), [], 0)

            for descriptor in r:
                if descriptor == self.socket:
                    descriptor, address = self.socket.accept()
                    if len(self.sockets) > 3:
                        descriptor.send("server full\n")
                        descriptor.close()
                        continue

                    cid = self.generate_id()
                    print "%s: connected" % cid
                    self.sockets[descriptor] = cid
                elif descriptor in self.sockets:
                    cid = self.sockets[descriptor]

                    try:
                        data = descriptor.recv(32)
                    except socket.error:
                        data = None

                    if not data:
                        print "%s: disconnected" % cid
                        del self.sockets[descriptor]
                    else:
                        for descriptor in self.sockets:
                            descriptor.send(data)
            time.sleep(1/20.0)


s = Server(("", 6660))
s.run()
