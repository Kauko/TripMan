import struct

def unpack_cid(data):
    #("!Bc", 1,'A', 320, 240)
    return struct.unpack("!cff", data)

def unpack_server_full(data):
    #("!B11s", 2, "server full")
    return struct.unpack("!11s", data)[0]

def unpack_position(data):
    #("!BcBff", 3, 'A', 1, 360.5, 450.4)
    return struct.unpack("!cBff", data)

def unpack_eat(data):
    #("!BcBff", 4, 'A', 1, 360.5, 450.4)
    return struct.unpack("!cBff", data)

def unpack_dead(data):
    #("!Bcff", 5, 'A', 360.5, 450.4)
    return struct.unpack("!cff", data)

def unpack_keyup(data):
    #("!BB", 6, 1)
    return struct.unpack("!B", data)[0]

def unpack_keydown(data):
    #("!BB", 7, 1)
    return struct.unpack("!B", data)[0]

unpackers = {'\x01': (9, unpack_cid),
             '\x02': (11, unpack_server_full),
             '\x03': (10, unpack_position),
             '\x04': (10, unpack_eat),
             '\x05': (9, unpack_dead),
             '\x06': (1, unpack_keyup),
             '\x07': (1, unpack_keydown)}

def get_unpacker(mid):
    return unpackers.get(mid, (None, None))


def pack_cid(cid, x, y):
    return struct.pack("!Bcff", 1, cid, x, y)

def pack_server_full():
    return struct.pack("!B11s", 2, "server full")

def pack_position(cid, direction, x, y):
    return struct.pack("!BcBff", 3, cid, direction, x, y)

def pack_eat(cid, drug, x, y):
    return struct.pack("!BcBff", 4, cid, drug, x, y)

def pack_dead(cid, x, y):
    return struct.pack("!Bcff", 5, cid, x, y)

def pack_keyup(key):
    return struct.pack("!BB", 6, key)

def pack_keydown(key):
    return struct.pack("!BB", 7, key)
