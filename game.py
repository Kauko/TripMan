# -*- coding: iso-8859-1 -*-
import time
import select
import socket

import pyglet
from pyglet.window import key

import cocos
from cocos.director import *
from cocos.scene import *
from cocos.layer import *
from cocos.sprite import *
from cocos.actions.interval_actions import * 
from cocos.actions.basegrid_actions import StopGrid
from cocos.actions.grid3d_actions import *
from cocos.menu import *
from cocos.text import *

import messages

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
        self.last = None
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(0)

    def read(self):
        r, _, _ = select.select([self.socket], [], [], 0)
        if r:
            mid = self.socket.recv(1)
            if not mid:
                return None, None

            length, unpacker = messages.get_unpacker(mid)
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
        self.alive = True

class PlayerLayer(ScrollableLayer):
    is_event_handler = True

    def __init__(self, width, height):
        super(PlayerLayer, self).__init__()
        self.px_width = width
        self.px_height = height
        self.delay = False

        self.schedule(self.update)
        self.schedule_interval(self.update_network, 1/60.0)
        
        self.cid = None
        
        self.movedir = 0 #1 = left,2 = up,3 = right,4 = down
        self.movespeed = 1
        self.players = dict()
        self.effects = None
        self.current_effect = 0

        self.sounds = dict()
        self.sounds[2] = pyglet.media.load("sounds/burb.wav", streaming=False)
        self.sounds[3] = pyglet.media.load("sounds/sniff.wav", streaming=False)
        self.sounds[4] = pyglet.media.load("sounds/gulp.wav", streaming=False)
        self.sounds[5] = pyglet.media.load("sounds/hehe.wav", streaming=False)
        self.sounds[6] = pyglet.media.load("sounds/wuhuu.wav", streaming=False)
        self.sounds[7] = pyglet.media.load("sounds/lighter.wav", streaming=False)

        self.reality = Sprite('pics/reality.png', position=(0,360), anchor=(1280, 360))
        self.add(self.reality, z=3)

        self.od = Sprite('pics/od.png', position=(800,360), anchor=(0,360))
        self.add(self.od, z=3)

        self.game_speed = 70;


    def on_key_press(self, key, modifiers):
        if key == LEFT:
            serverConnection.write(messages.pack_keydown(MOVELEFT))
        elif key == RIGHT:
            serverConnection.write(messages.pack_keydown(MOVERIGHT))
        elif key == UP:
            serverConnection.write(messages.pack_keydown(MOVEUP))
        elif key == DOWN:
            serverConnection.write(messages.pack_keydown(MOVEDOWN))

    def on_key_release(self, key, modifiers):
        if key == LEFT:
            serverConnection.write(messages.pack_keyup(MOVELEFT))
        elif key == RIGHT:
            serverConnection.write(messages.pack_keyup(MOVERIGHT))
        elif key == UP:
            serverConnection.write(messages.pack_keyup(MOVEUP))
        elif key == DOWN:
            serverConnection.write(messages.pack_keyup(MOVEDOWN))

    def update(self, dt):
        if self.delay != False and time.time() > self.delay:
            self.reality.x += self.game_speed * dt
            self.od.x += self.game_speed * dt

        player = self.players.get(self.cid, None)
        if player:
            (x, y) = player.position
            if y > 360 and y < 360 + 720:
                self.reality.y = y 
                self.od.y = y

            if x < self.reality.x or x > self.od.x:
                if player.alive:
                    serverConnection.write(messages.pack_death(player.cid, x, y))
                    player.alive = False

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
                if effect == 2:
                    current_effect = Liquid(waves=5, amplitude=40, 
                                            grid=(16,16), duration=10)
                elif effect == 3:
                    current_effect = Liquid(waves=5, amplitude=40, 
                                            grid=(16,16), duration=10)
                elif effect == 4:
                    current_effect = Liquid(waves=5, amplitude=40, 
                                            grid=(16,16), duration=10)
                elif effect == 5:
                    current_effect = Liquid(waves=5, amplitude=40, 
                                            grid=(16,16), duration=10)
                elif effect == 6:
                    current_effect = Liquid(waves=5, amplitude=40, 
                                            grid=(16,16), duration=10)
                elif effect == 7:
                    current_effect = Liquid(waves=5, amplitude=40, 
                                            grid=(16,16), duration=10)

                self.get_ancestor(GameLevelScene).do(current_effect+StopGrid())
                self.get_ancestor(GameLevelScene).boosts[(x,y)].visible = False

                if effect in self.sounds:
                    self.sounds[effect].play()

        elif mid == 5:
            cid, x, y = data
            if cid == self.cid:
                print "I'm dead"
                director.replace(GameOverScene())
            else:
                player = self.players.get(cid, None)
                if player:
                    player.visible = False
        elif mid == 8:
            self.delay = data

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

        pyglet.media.load('sounds/music.wav', streaming=False).play()
        if serverConnection.socket and serverConnection.socket.recv(20):
            serverConnection.close()
        serverConnection.connect()

class GameOverScene(Scene):
    def __init__(self):
        super(GameOverScene, self).__init__()
        self.add(ColorLayer(255, 0, 0, 255))
        self.add(GameOverLayer(), z=1)


class GameOverLayer(Layer):
    is_event_handler = True
    def __init__(self):
        x, y = director.get_window_size()
        super(GameOverLayer, self).__init__()
        
        self.gameOver = Label("GAME OVER!", font_size=40,
                          font_name='arial',
                          color=(0, 0, 0, 255),
                          anchor_x='center',
                          anchor_y='bottom')
        self.gameOver.position = (x / 2, y /2)
        self.add(self.gameOver)

    def on_key_release(self, symbol, modifiers):
        if symbol == key.ENTER:
            director.pop()

class MainMenu(Menu):

    def __init__(self):
        super(MainMenu, self).__init__('')
        #self.add(ColorLayer(0, 127, 255, 255), z=-1)
        self.menu_anchor_y = CENTER
        self.menu_anchor_x = CENTER
        
        items = [
            MenuItem('New Game', self.on_new_game),
            MenuItem('Credits', self.on_credits),
            MenuItem('Quit', self.on_quit),
            ]

        self.create_menu(items, zoom_in(), zoom_out(), zoom_out())
        
    def on_new_game(self):
        director.push(GameLevelScene())

    def on_quit(self):
        exit()

    def on_credits(self):
        self.parent.switch_to(1)

class Credits(ColorLayer):

    is_event_handler = True

    def __init__(self):
        super(Credits, self).__init__(0, 127, 255, 255)

        INTRO = """<b>TripMan<b>

<p>
<i>Team:</i><br>
Rauli Puuper&auml;<br>
Sebastian Turpeinen<br>
Teemu Kaukoranta<br>
Miikka Saukko<br>
</p>
<p>
<i>Special Thanks:</i><br>
Mika Sepp&auml;nen<br>
</p>
<p>
<i>Extra Special Thanks</i><br>
The lovely organizers of Vectorama 2012 <3<3<3<3</p>
"""
        self.introlabel = cocos.text.HTMLLabel(INTRO,
                                                x=1280/3,
                                                y=2 * 720/ 3,
                                                anchor_x='left',
                                                multiline=True,
                                                width=self.width - 200)

        self.add(self.introlabel)

    def on_key_press(self, key, modifier):
        self.parent.switch_to(0)
        return True
        
def exit():
    pyglet.app.exit()
    print 'Thank you for playing'
        
if __name__ == '__main__':
    serverConnection = ServerConnection('shell.jkry.org', 10066)
    director.init(width=1280, height=720)#, fullscreen=True)
    scene = Scene()
    scene.add(MultiplexLayer(MainMenu(), Credits()), z=1)
    director.run(scene)

