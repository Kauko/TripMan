import time
import select
import socket

import pyglet
from pyglet.gl import *

import cocos
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
        
        self.movement = [0, 0]
        self.cid = 1
        self.players = dict()
        
        self.reality = Sprite('reality.png', position=(10,0), anchor=(1280, 0))
        self.add(self.reality, z=3)

        self.od = Sprite('od.png', position=(300,0), anchor=(0,0))
        self.add(self.od, z=3)

        self.game_speed = 10;

        player = Sprite("test.png", position=(320,240))
        self.add(player)
        self.players[self.cid] = player

    def on_key_press(self, key, modifiers):
        self.chars_pressed.add(key)

    def on_key_release(self, key, modifiers):
        self.chars_pressed.remove(key)

    def update(self, dt):
        self.reality.x += self.game_speed * dt
        self.od.x += self.game_speed * dt

        player = self.players.get(self.cid, None)
        if player.y > 315 and player.y < 315 + 720:
            self.reality.y = player.y - 320
            self.od.y = player.y - 320

        if not player:
            print "No player"
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
        player.position = (x, y)
        self.get_ancestor(ScrollingManager).set_focus(x, y)
        

class GameLevelScene(Scene):
    def __init__(self):
        super(GameLevelScene, self).__init__()
        self.scroller = ScrollingManager()
        bglayer = ScrollableLayer()
        bglayer.px_width = 2600
        bglayer.px_height = 1480

        f = open('level1.txt', "r")
        worldGrid = []
        for line in f:
            line = line.replace('\n','')
            worldGrid.append(list(line))
        print(worldGrid)
        bglayer.add(Sprite('background.png', position=(1300, 360)))
        bglayer.add(Sprite('background.png', position=(1300, 360+720)))
        
        tiles = cocos.batch.BatchNode()
        level = loadLevel('level2.txt')
        print 'lll', level
        for i, line in enumerate(level):
            for j, code in enumerate(line):
                if code == '1':
                    tile = Sprite('brickwall.png')
                    tile.position = (i*40 + 20, (720 * 2 - j*40) - 20)
                    tiles.add(tile)
        bglayer.add(tiles, z=1)
        self.scroller.add(bglayer)


        self.scroller.add(PlayerLayer(2600, 1480, (320, 200)), z=1)
        self.add(self.scroller)

def loadLevel(filename):
    level = list()
    for line in open(filename):
        row = list()
        for char in line.strip():
            row.append(char)
        level.append(row)
    return level

if __name__ == '__main__':
    director.init(width=1240, height=720)
    director.run(GameLevelScene())
