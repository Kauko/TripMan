import time
import select
import socket

import pyglet

from cocos.director import *
from cocos.scene import *
from cocos.layer import *
from cocos.sprite import *

from messages import get_unpacker, pack_position, pack_eat, pack_dead

LEFT = 65361
UP = 65362
RIGHT = 65363
DOWN = 65364
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
            self.socket.send(data)

class PlayerLayer(ScrollableLayer):
    is_event_handler = True

    def __init__(self, width, height, start_position):
        super(PlayerLayer, self).__init__()
        print(start_position)
        self.px_width = width
        self.px_height = height
        
        self.chars_pressed = set()
        self.schedule(self.update)
        self.schedule_interval(self.update_network, 1/20.0)
        
        self.movement = [0, 0]
        self.sprites = dict()
        self.cid = None

    def on_key_press(self, key, modifiers):
        self.chars_pressed.add(key)

    def on_key_release(self, key, modifiers):
        self.chars_pressed.remove(key)

    def update(self, dt):
        pass

    def update_network(self, dt):

        #read networkstuff
        mid, data = serverConnection.read()
        if mid:
            print repr(mid), repr(data)
        if mid == 1:
            self.cid = data
            sprite = Sprite('test.png', position=(320,240))
            self.add(sprite)
            #self.movement = [320, 240]
            self.sprites[self.cid] = sprite
        elif mid == 3:
            cid, direction, x, y = data
            sprite = self.sprites.get(cid, None)
            if not sprite:
                sprite = Sprite('test.png', position=(320,240))
                self.add(sprite)
                self.sprites[cid] = sprite
            sprite.position = (x, y)
            self.get_ancestor(ScrollingManager).set_focus(x, y)
            #print time.time(), "POSITION", data

        #write position
        if self.cid is not None:
            player = self.sprites.get(self.cid, None)
            x, y = player.position
            nx, ny = self.movement
            
            if x != nx or y != ny:
                if self.cid:
                    position = pack_position(self.cid, 1, nx, ny)
                    serverConnection.write(position)

        player = self.sprites.get(self.cid, None)
        if not player:
            return

        x, y = player.position
            
        if LEFT in self.chars_pressed:
            x -= 200 * dt
        if UP in self.chars_pressed:
            y += 200 * dt
        if RIGHT in self.chars_pressed:
            x += 200 * dt
        if DOWN in self.chars_pressed:
            y -= 200 * dt

        print x, y
        self.movement = [x, y]

        

class GameLevelScene(Scene):
    def __init__(self):
        super(GameLevelScene, self).__init__()
        self.scroller = ScrollingManager()
        bglayer = ScrollableLayer()
        f = open('level1.txt', "r")
        worldGrid = []
        for line in f:
            line = line.replace('\n','')
            worldGrid.append(list(line))
        print(worldGrid)
        bglayer.add(Sprite('background.png', position=(1300, 360)))
        self.scroller.add(bglayer)
        for sublist in worldGrid:
            for char in sublist:
                if char == 'A':
                    print("derp")
                    self.scroller.add(PlayerLayer(2600, 720, (worldGrid.index(sublist),sublist.index(char))), z=1)
                         
        
        self.add(self.scroller)

if __name__ == '__main__':
    serverConnection = ServerConnection('shell.jkry.org', 10066)
    director.init(width=1240, height=720)
    director.run(GameLevelScene())
