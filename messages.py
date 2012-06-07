import struct

parsers = {1: (36, cid),
           2: (11, server_full),
           3: (45, position),
           4: (45, eat),
           5: (44, dead)}

def cid(data):
    #("!B36s", 1,'51d2f4b2-4533-4c58-90e6-72d554b52831')
    return struct.unpack("!36s", data)[0]

def server_full(data):
    #("!B11s", 2, "server full")
    return struct.unpack("!11s", data)[0]

def position(data):
    #("!B36sBII", 3, '51d2f4b2-4533-4c58-90e6-72d554b52831', 1, 360, 450)
    return struct.unpack("!36sBII", data)

def eat(data):
    #("!B36sBII", 4, '51d2f4b2-4533-4c58-90e6-72d554b52831', 1, 360, 450)
    return struct.unpack("!36sBII", data)

def dead(data):
    #("!B36sII", 5, '51d2f4b2-4533-4c58-90e6-72d554b52831', 360, 450)
    return struct.unpack("!36sII", data)
