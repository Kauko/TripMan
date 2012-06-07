import select
import socket

from cocos.director import *
from cocos.scene import *
from cocos.layer import *
from cocos.sprite import *

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
            return self.socket.recv(1024)

    def write(self, data):
        
        self.socket.send(data)

class BackgroundLayer (ColorLayer):
    is_event_handler = True
    def __init__(self):
        super(BackgroundLayer, self).__init__(0, 0, 100, 255)
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
          serverConnection.write(str((y, y)))
      self.sprite.position = (x, y)

      #read networkstuff
      data = serverConnection.read()
      if data:
          print data




if __name__ == '__main__':
    serverConnection = ServerConnection('localhost', 6660)
    director.init()
    director.run(Scene(BackgroundLayer()))
