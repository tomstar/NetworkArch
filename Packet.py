class Packet(object):

    def __init__(self, dest, source, path=None):
        self.destination = dest
        self.source = source
        self.path = path
        self.transitTime = 1


class ControlPacket(Packet):

    def __init__(self, dest, source, table, path=None):
        super(ControlPacket, self).__init__(dest, source, path)
        self.RoutingTable = table
        

class DataPacket(Packet):
    pass
