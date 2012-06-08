import time
import select
import socket

import pyglet

from cocos.director import *
from cocos.scene import *
from cocos.layer import *
from cocos.sprite import *
from cocos.actions.interval_actions import MoveTo

from messages import get_unpacker, pack_keyup, pack_keydown

LEFT = 65361
UP = 65362
RIGHT = 65363
DOWN = 65364

MOVELEFT = 1
MOVERIGHT = 3
MOVEUP = 2
MOVEDOWN = 4

TILEWIDTH = 16
TILEHEIGHT = 16

class ServerConnection(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.connect((host, port))
        self.socket.setblocking(0)
        self.last = None

    def read(self):
        r, _, _ = select.select([self.socket], [], [], 0)
        if r:
            mid = self.socket.recv(1)
            if not mid:
                return None, None

            length, unpacker = get_unpacker(mid)
            if length:
                data = self.socket.recv(length)
                unpacked = unpacker(data)
                return ord(mid), unpacked

        return None, None

    def write(self, data):
        if data != self.last:
            self.last = data
            print "ding", repr(data)
            self.socket.send(data)

class Player(Sprite):
    def __init__(self, cid, image, position):
        Sprite.__init__(self, image, position=position)
        self.cid = cid
        self.target = self.position
        self.moveto = None

class PlayerLayer(ScrollableLayer):
    is_event_handler = True

    def __init__(self, width, height):
        super(PlayerLayer, self).__init__()
        self.px_width = width
        self.px_height = height
        
        self.schedule(self.update)
        self.schedule_interval(self.update_network, 1/20.0)
        
        self.cid = None
        
        self.movedir = 0 #1 = left,2 = up,3 = right,4 = down
        self.movespeed = 1
        self.players = dict()

    def on_key_press(self, key, modifiers):
        print key
        if key == LEFT:
            serverConnection.write(pack_keydown(MOVELEFT))
        elif key == RIGHT:
            serverConnection.write(pack_keydown(MOVERIGHT))
        elif key == UP:
            serverConnection.write(pack_keydown(MOVEUP))
        elif key == DOWN:
            serverConnection.write(pack_keydown(MOVEDOWN))

    def on_key_release(self, key, modifiers):
        if key == LEFT:
            serverConnection.write(pack_keyup(MOVELEFT))
        elif key == RIGHT:
            serverConnection.write(pack_keyup(MOVERIGHT))
        elif key == UP:
            serverConnection.write(pack_keyup(MOVEUP))
        elif key == DOWN:
            serverConnection.write(pack_keyup(MOVEDOWN))

    def update(self, dt):
        player = self.players.get(self.cid, None)
        if player:
            (x, y) = player.position 
            self.get_ancestor(ScrollingManager).set_focus(int(x), int(y))

    def update_network(self, dt):
        #read networkstuff
        mid, data = serverConnection.read()
        if mid:
            print repr(mid), repr(data)
        if mid == 1:
            self.cid = data
            player = Player(self.cid, "test.png", (320,240))
            self.add(player)
            self.players[self.cid] = player
        elif mid == 3:
            cid, direction, x, y = data
            player = self.players.get(cid, None)
            if not player:
                player = Player(cid, "test.png", (x,y))
                self.add(player)
                self.players[cid] = player

            if player.moveto:
                player.moveto.stop()
            player.moveto = MoveTo((x,y), 1/20.0)
            player.do(player.moveto)

#        #write position
#        player = self.players.get(self.cid, None)
#        if player:
#            x, y = player.target 
#            position = pack_position(self.cid, 1, x, y)
#            serverConnection.write(position)

class GameLevelScene(Scene):
    def __init__(self):
        super(GameLevelScene, self).__init__()
        self.scroller = ScrollingManager()
        bglayer = ScrollableLayer()
        bglayer.add(Sprite('background.png', position=(1300, 360)))
        self.scroller.add(bglayer)
        self.scroller.add(PlayerLayer(2600, 720), z=1)
        self.add(self.scroller)
        
if __name__ == '__main__':
    serverConnection = ServerConnection('', 10066)
    director.init(width=1240, height=720)
    director.run(GameLevelScene())
