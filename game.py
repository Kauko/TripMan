import time
import select
import socket

import pyglet

import cocos
from cocos.director import *
from cocos.scene import *
from cocos.layer import *
from cocos.sprite import *
from cocos.actions.interval_actions import * 
from cocos.actions.basegrid_actions import StopGrid
from cocos.actions.grid3d_actions import *
from messages import get_unpacker, pack_keyup, pack_keydown
from testing import GameLevelScene

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

E_RIPPLE = 2
E_LENS = 3
E_LIQUID = 4
E_SHAKY = 5
E_TWIRL = 6
E_WAVES = 7

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

class Player(Sprite):
    def __init__(self, cid, image, position):
        Sprite.__init__(self, image, position=position)
        self.cid = cid
        self.moveto = None

class PlayerLayer(ScrollableLayer):
    is_event_handler = True

    def __init__(self, width, height):
        super(PlayerLayer, self).__init__()
        self.px_width = width
        self.px_height = height
        
        self.schedule(self.update)
        self.schedule_interval(self.update_network, 1/60.0)
        
        self.cid = None
        
        self.movedir = 0 #1 = left,2 = up,3 = right,4 = down
        self.movespeed = 1
        self.players = dict()
        self.effects = None
        self.current_effect = 0

#        self.effects = {2: FlipY3D(grid=(1,1),duration=10),
#                        3: Shaky3D( randrange=6, grid=(4,4), duration=10),
#                        4: Liquid(waves=5, amplitude=40, grid=(16,16),
#                           duration=10),
#                        5: Twirl( center=(320,240), twirls=5, amplitude=1,
##                           grid=(16,12), duration=10),
#                        6: Waves( waves=4, amplitude=20, hsin=False, 
#                           vsin=True, grid=(16,16), duration=10)}
    
        self.reality = Sprite('pics/reality.png', position=(5,0), anchor=(1280, 0))
        self.add(self.reality, z=3)

        self.od = Sprite('pics/od.png', position=(745,0), anchor=(0,0))
        self.add(self.od, z=3)

        self.game_speed = 15;


    def on_key_press(self, key, modifiers):
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
        self.reality.x += self.game_speed * dt
        self.od.x += self.game_speed * dt

        player = self.players.get(self.cid, None)
        if player:
            if player.y > 315 and player.y < 315 + 720:
                self.reality.y = player.y - 320
                self.od.y = player.y - 320

            (x, y) = player.position 
            self.get_ancestor(ScrollingManager).set_focus(int(x), int(y))

    def update_network(self, dt):
        #read networkstuff
        mid, data = serverConnection.read()
        if mid == 1:
            print repr(mid), repr(data)
        if mid == 1:
            self.cid, x, y = data
            x = x * 40 + 20
            y = y * 40 + 20
            player = Player(self.cid, "pics/" + self.cid + ".png", (x,y))
            self.add(player)
            self.players[self.cid] = player
        elif mid == 3:
            cid, direction, x, y = data
            player = self.players.get(cid, None)
            
            x = x * 40 + 20
            y = y * 40 + 20 # nolla = alareuna tiedostalla ja kasvaa yloes
            if not player:
                player = Player(cid, "pics/" + cid + ".png", (x,y))
                self.add(player)
                self.players[cid] = player

            if player.moveto:
                player.moveto.stop()
            player.moveto = MoveTo((x,y), 1/20.0)
            player.do(player.moveto)
        
        elif mid == 4:
            cid,effect, x, y = data
            if effect != 0 and self.get_ancestor(GameLevelScene).boosts[(x,y)].visible:
                if self.current_effect:
                    print "halt"
                    #self.current_effect.stop()
                    #self.get_ancestor(GameLevelScene).do(StopGrid())

                if effect == 2:
                    current_effect = FlipY3D(grid=(1,1),duration=10)
                elif effect == 3:
                    current_effect = Shaky3D(randrange=6, grid=(4,4),
                                                  duration=10)
                elif effect == 4:
                    current_effect = Liquid(waves=5, amplitude=40, 
                                                 grid=(16,16), duration=10)
                elif effect == 5:
                    current_effect = Twirl(center=(320,240), twirls=5,
                                                amplitude=1, grid=(16,12),
                                                duration=10)
                elif effect == 6:
                    current_effect = Waves(waves=4, amplitude=20, 
                                                hsin=False, vsin=True, 
                                                grid=(16,16), duration=10)

#                self.current_effect = self.effects[effect]
                self.get_ancestor(GameLevelScene).do(current_effect+StopGrid())
                
                self.get_ancestor(GameLevelScene).boosts[(x,y)].visible = False

def loadLevel(filename):
    level = list()
    for line in open(filename):
        row = list()
        for char in line.strip():
            row.append(char)
        level.append(row)
    return level


class GameLevelScene(Scene):
    def __init__(self):
        super(GameLevelScene, self).__init__()
        self.scroller = ScrollingManager()
 
        tiles = cocos.batch.BatchNode()
        self.boosts = {}
        level = loadLevel('levels/level2.txt')
        width = 1280
        bglayer = ScrollableLayer()
        for j, line in enumerate(level[::-1]):
            width = len(line)
            for i, code in enumerate(line):
                if code == '1':
                    tile = Sprite('pics/brickwall.png')
                    tile.position = (i*40 + 20, (j*40+20))
                    tiles.add(tile)
                elif code == '2':
                    boost = Sprite('pics/bottle.png')
                    boost.position = (i*40 + 20, (j*40+20))
                    self.boosts[(i,j)]=boost
                    bglayer.add(boost, z=2)
                elif code == '3':
                    boost = Sprite('pics/cocaine.png')
                    boost.position = (i*40 + 20, (j*40+20))
                    self.boosts[(i,j)]=boost
                    bglayer.add(boost, z=2)
                elif code == '4':
                    boost = Sprite('pics/pill.png')
                    boost.position = (i*40 + 20, (j*40+20))
                    self.boosts[(i,j)]=boost
                    bglayer.add(boost, z=2)
                elif code == '5':
                    boost = Sprite('pics/stamp.png')
                    boost.position = (i*40 + 20, (j*40+20))
                    self.boosts[(i,j)]=boost
                    bglayer.add(boost, z=2)
                elif code == '6':
                    boost = Sprite('pics/syringe.png')
                    boost.position = (i*40 + 20, (j*40+20))
                    self.boosts[(i,j)]=boost
                    bglayer.add(boost, z=2)
                elif code == '7':
                    boost = Sprite('pics/joint.png')
                    boost.position = (i*40 + 20, (j*40+20))
                    self.boosts[(i,j)]=boost
                    bglayer.add(boost, z=2)
        width = width*40
        bglayer.px_width = width
        bglayer.px_height = 1440

        bglayer.add(tiles, z=1)
        self.scroller.add(bglayer)

        self.scroller.add(PlayerLayer(width, 1440), z=1)
        self.add(self.scroller)
        
if __name__ == '__main__':
    serverConnection = ServerConnection('localhost', 10066)
    director.init(width=1280, height=720)#, fullscreen=True)
    director.run(GameLevelScene())
