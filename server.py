import time
import random
import socket
from select import select
from messages import get_unpacker, pack_cid, pack_server_full, pack_position

MOVELEFT = 1
MOVERIGHT = 3
MOVEUP = 2
MOVEDOWN = 4


class Player:
    def __init__(self, cid, position):
        self.cid = cid
        self.position = position
        self.direction = 1
        self.velocity = 0

class Server:
    def __init__(self, address):
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(0)
        self.socket.bind(self.address)
        self.running = False
        self.sockets = dict()
        self.players = dict()

        f = open('level1.txt', "r")
        lines = f.readlines()
        f.close()

        self.worldGrid = []
        for index in range(len(lines)):
            self.worldGrid.insert(0, list(lines[index].strip()))

        self.start_points = dict()
        for cid in ["A", "B","C","D"]:
            self.start_points[cid] = self.getPlayerStartPosition(cid)
            print "START", self.start_points[cid]

    def descriptors(self):
        yield self.socket

        for descriptor in self.sockets:
            yield descriptor

    def generate_id(self):
        return 'A'
        cid = chr(random.randint(65,68))
        while cid in self.sockets.values():
            cid = chr(random.randint(65,68))
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
                    position = self.start_points["A"] 
                    player = Player(cid, position)
                    self.sockets[descriptor] = player
                    descriptor.send(pack_cid(cid))
                elif descriptor in self.sockets:
                    player = self.sockets[descriptor]

                    mid, data = None, None
                    try:
                        mid = descriptor.recv(1)
                        if mid:
                            length, unpacker = get_unpacker(mid)
                            if length:
                                data = descriptor.recv(length)
                                if ord(mid) == 6: #key up
                                    key = unpacker(data)
                                    player.velocity = 0
                                    print "KEYUP", key, player.velocity
                                elif ord(mid) == 7: #key down
                                    key = unpacker(data)
                                    print "KEYDOWN", key
                                    player.direction = key
                                    player.velocity = 1
                    except socket.error, err:
                        print "socket.error", repr(err)

            for descriptor in self.sockets:
                player = self.sockets[descriptor]
                if player.velocity:
                    if self.isMoveLegal(player, player.direction):
                        if player.direction == MOVELEFT:
                            player.position = player.position[0]-1, player.position[1]
                        elif player.direction == MOVERIGHT:
                            player.position = player.position[0]+1, player.position[1]
                        elif player.direction == MOVEUP:
                            player.position = player.position[0], player.position[1]+1
                        elif player.direction == MOVEDOWN:
                            player.position = player.position[0], player.position[1]-1

                        for foo in self.sockets:
                            descriptor.send(pack_position(player.cid, 
                                                          player.direction,
                                                          player.position[0],
                                                          player.position[1]))

    def isMoveLegal(self, player, movedir):
        x, y = player.position
        if movedir == MOVELEFT:
            if self.worldGrid[y][x-1] == "1" or x <= 0:
                return False
            else:
                return True
        elif movedir == MOVEUP:
            try:
                if self.worldGrid[y+1][x] == "1" or y >= len(self.worldGrid)-1:
                    return False
                else:
                    return True
            except IndexError:
                return False
        elif movedir == MOVERIGHT:
            try:
                if self.worldGrid[y][x+1] == "1" or x >= len(self.worldGrid[0])-1:
                    return False
                else:
                    return True
            except IndexError:
                return False
        elif movedir == MOVEDOWN:
            if self.worldGrid[y-1][x] == "1" or y <= 0:
                return False
            else:
                return True
        else:
            return False

    def getPlayerStartPosition(self, cid):
        for index, row in enumerate(self.worldGrid):
            for jindex, col in enumerate(row):
                if col == cid:
                    return (jindex, index)

if __name__ == "__main__":
    s = Server(("", 10066))
    s.run()
