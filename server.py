import time
import uuid
import socket
from select import select

class Client:
    def __init__(self, cid, socket, address):
        self.cid = cid
        self.socket = socket
        self.address = address

class Server:
    def __init__(self, address):
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(0)
        self.socket.bind(self.address)
        self.running = False
        self.clients = dict()
        self.sockets = dict()

    def descriptors(self):
        yield self.socket

        for descriptor in self.sockets:
            yield descriptor

    def generate_id(self):
        cid = str(uuid.uuid4())
        while cid in self.clients:
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
                    if len(self.clients) > 3:
                        descriptor.send("server full\n")
                        descriptor.close()
                        continue

                    cid = self.generate_id()
                    client = Client(cid, descriptor, address)
                    print "%s: connected" % client.cid
                    self.clients[cid] = client
                    self.sockets[descriptor] = client
                elif descriptor in self.sockets:
                    client = self.sockets[descriptor]

                    data = descriptor.recv(32)
                    if not data:
                        print "%s: disconnected" % client.cid
                        del self.clients[client.cid]
                        del self.clients[descriptor]
                    else:
                        for descriptor in self.sockets:
            time.sleep(1/20.0)


s = Server(("", 6660))
s.run()
