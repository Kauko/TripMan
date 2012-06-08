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

class ServerConnection(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.connect((host, port))
        self.socket.setblocking(0)

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
                return mid, unpacked

        return None, None

    def write(self, data):
        self.socket.send(data)

class PlayerLayer(ScrollableLayer):
    is_event_handler = True

    def __init__(self, width, height):
        super(PlayerLayer, self).__init__()
        self.px_width = width
        self.px_height = height
        
        self.sprite = Sprite('test.png', position=(320,240))  
        self.add(self.sprite)  
        self.chars_pressed = set()
        self.schedule(self.update)

    def on_key_press(self, key, modifiers):
        self.chars_pressed.add(key)

    def on_key_release(self, key, modifiers):
        self.chars_pressed.remove(key)

    def update(self, dt):
        x, y = self.sprite.position
        if LEFT in self.chars_pressed:
            x -= 2
        if UP in self.chars_pressed:
            y += 2
        if RIGHT in self.chars_pressed:
            x += 2
        if DOWN in self.chars_pressed:
            y -= 2
        if x != self.sprite.position[0] or y != self.sprite.position[1]:
            position = pack_position("Q", 1, x, y)
            serverConnection.write(position)
            self.sprite.position = (x, y)
            self.get_ancestor(ScrollingManager).set_focus(x, y)

        #read networkstuff
        mid, data = serverConnection.read()
        if data:
            print data

class GameLevelScene(Scene):
    def __init__(self):
        super(GameLevelScene, self).__init__()
        self.scroller = ScrollingManager()
        bglayer = ScrollableLayer()
#        bglayer.add(Sprite('background.png', position=(1300, 360)))
#        self.scroller.add(bglayer)
        self.scroller.add(PlayerLayer(2600, 720), z=1)
        self.add(self.scroller)

if __name__ == '__main__':
    serverConnection = ServerConnection('localhost', 6660)
    director.init(width=1240, height=720)
    director.run(GameLevelScene())
