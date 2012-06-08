import struct

def unpack_cid(data):
    #("!Bc", 1,'A')
    return struct.unpack("!c", data)[0]

def unpack_server_full(data):
    #("!B11s", 2, "server full")
    return struct.unpack("!11s", data)[0]

def unpack_position(data):
    #("!BcBII", 3, 'A', 1, 360, 450)
    return struct.unpack("!cBII", data)

def unpack_eat(data):
    #("!BcBII", 4, 'A', 1, 360, 450)
    return struct.unpack("!cBII", data)

def unpack_dead(data):
    #("!BcII", 5, 'A', 360, 450)
    return struct.unpack("!cII", data)

unpackers = {'\x01': (1, unpack_cid),
             '\x02': (11, unpack_server_full),
             '\x03': (10, unpack_position),
             '\x04': (10, unpack_eat),
             '\x05': (9, unpack_dead)}

def get_unpacker(mid):
    return unpackers.get(mid, (None, None))


def pack_cid(cid):
    return struct.pack("!Bc", 1, cid)

def pack_server_full():
    return struct.pack("!B11s", 2, "server full")

def pack_position(cid, direction, x, y):
    return struct.pack("!BcBII", 3, cid, direction, x, y)

def pack_eat(cid, drug, x, y):
    return struct.pack("!BcBII", 3, cid, drug, x, y)

def pack_dead(cid, x, y):
    return struct.pack("!cII", cid, x, y)

