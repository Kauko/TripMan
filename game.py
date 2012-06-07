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
      self.sprite.position = (x, y)


def connectToServer(address):
    print "connecting to", address

if __name__ == '__main__':
    connectToServer("127.0.0.1")
    director.init()
    director.run(Scene(BackgroundLayer()))
