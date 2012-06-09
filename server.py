import time
import random
import socket
from select import select
import messages

MOVELEFT = 1
MOVERIGHT = 3
MOVEUP = 2
MOVEDOWN = 4

E_RIPPLE = 2
E_LENS = 3
E_LIQUID = 4
E_SHAKY = 5
E_TWIRL = 6
E_WAVES = 7

E_WIN = 9

class Player:
    def __init__(self, cid, position):
        self.cid = cid
        self.position = position
        self.direction = 1
        self.velocity = 0
        self.effect = 0
        self.alive = True 

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

        f = open('levels/level2.txt', "r")
        lines = f.readlines()
        f.close()

        self.worldGrid = []
        for index in range(len(lines)):
            self.worldGrid.insert(0, list(lines[index].strip()))

        self.start_points = dict()

        for cid in ["A", "B", "C", "D"]:
            self.start_points[cid] = self.getPlayerStartPosition(cid)

    def descriptors(self):
        yield self.socket

        for descriptor in self.sockets:
            yield descriptor

    def generate_id(self):
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
            start = time.time()
            r, w, x = select(self.descriptors(), [], [], 0)

            for descriptor in r:
                if descriptor == self.socket:
                    descriptor, address = self.socket.accept()
                    if len(self.sockets) > 3:
                        descriptor.send(messages.pack_server_full())
                        descriptor.close()
                        continue

                    cid = self.generate_id()
                    print "%s: connected" % cid
                    position = self.start_points[cid] 
                    player = Player(cid, position)
                    self.sockets[descriptor] = player
                    descriptor.send(messages.pack_cid(cid, position[0], position[1]))
                elif descriptor in self.sockets:
                    player = self.sockets[descriptor]

                    mid, data = None, None
                    try:
                        mid = descriptor.recv(1)
                        if mid:
                            length, unpacker = messages.get_unpacker(mid)
                            if length:
                                data = descriptor.recv(length)
                                if ord(mid) == 5:
                                    player.alive = False
                                elif ord(mid) == 6: #key up
                                    player.velocity = 0
                                elif ord(mid) == 7: #key down
                                    key = unpacker(data)
                                    player.direction = key
                                    player.velocity = 1
                        else:
                            print "%s: disconnected" % player.cid
                            del self.sockets[descriptor]
                    except socket.error, err:
                        print "socket.error", repr(err)

            remove = set()
            for descriptor in self.sockets:
                player = self.sockets[descriptor]
                if player.velocity:
                    if self.isMoveLegal(player, player.direction):
                        x,y = player.position
                        if player.direction == MOVELEFT:
                            player.position = x-1, y 
                        elif player.direction == MOVERIGHT:
                            player.position = x+1, y 
                        elif player.direction == MOVEUP:
                            player.position = x, y+1
                        elif player.direction == MOVEDOWN:
                            player.position = x, y-1
                        
                        self.checkTile(player)
                        
                        pos_msg = messages.pack_position(player.cid,
                                                         player.direction,
                                                         player.position[0],
                                                         player.position[1])
                        for client in self.sockets:
                            try:
                                client.send(pos_msg)
                            except socket.error, err:
                                remove.add(client)
                        
                if player.effect:
                    eat_msg = messages.pack_eat(player.cid,
                                                player.effect,
                                                player.position[0],
                                                player.position[1])
                    for client in self.sockets:
                        try:
                            client.send(eat_msg)
                        except socket.error, err:
                            remove.add(client)
                    player.effect = 0

                if not player.alive:
                    death_msg = messages.pack_death(player.cid,
                                                    player.position[0],
                                                    player.position[1])
                    for client in self.sockets:
                        try:
                            client.send(death_msg)
                        except socket.error, err:
                            remove.add(client)

            for client in remove:
                try:
                    del self.sockets[client]
                except KeyError:
                    pass
            snooze = 1/20.0 - (time.time()-start)
            if snooze > 0:
                time.sleep(snooze)

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

    def checkTile(self, player):
        x,y = player.position
        if self.worldGrid[y][x] != '0':
            if self.worldGrid[y][x] == str(E_RIPPLE):
                player.effect = E_RIPPLE
            elif self.worldGrid[y][x] == str(E_LENS):
                player.effect = E_LENS
            elif self.worldGrid[y][x] == str(E_LIQUID):
                player.effect = E_LIQUID
            elif self.worldGrid[y][x] == str(E_SHAKY):
                player.effect = E_SHAKY
            elif self.worldGrid[y][x] == str(E_TWIRL):
                player.effect = E_TWIRL
            elif self.worldGrid[y][x] == str(E_WAVES):
                player.effect = E_WAVES
            elif self.worldGrid[y][x] == str(E_WIN):
                player.effect = E_WIN
            else:
                player.effect = 0
        else:
            player.effect = 0
    
    def getPlayerStartPosition(self, cid):
        for index, row in enumerate(self.worldGrid):
            for jindex, col in enumerate(row):
                if col == cid:
                    return (jindex, index)

if __name__ == "__main__":
    s = Server(("", 10066))
    s.run()
