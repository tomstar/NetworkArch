class Packet(object):

    def __init__(self, dest, source, table=None, path=None):
        self.destination = dest
        self.source = source
        self.path = path
        self.transitTime = 1
        self.RoutingTable = table
        self.nextHop = None

    def cycle(self):
        self.transitTime = self.transitTime-1
        print("Packet waiting")


class ControlPacket(Packet):

    def __init__(self, dest, source, table, path=None):
        super(ControlPacket, self).__init__(dest, source, table, path)


class DataPacket(Packet):
    def __init__(self, dest, source, table, data, path):
        super(DataPacket, self).__init__(dest, source, table, path)
        self.data = data
