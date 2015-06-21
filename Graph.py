#!/usr/bin/python3
import pickle
import copy

import Exceptions as ex


class Graph(set):
    """
    Graph class containing Nodes and Edges.

    Edges can be unidirectional with different weight for the directions.
    """
    def __init__(self):
        super(Graph, self).__init__(self)
        self._nodes = []

    def store(self, filename):
        pickle.dump(self, open(filename, 'bw'))

    def updateRoutingTables(self):
        for node in self.nodes:
            node.updateTableFromConnections()

    def __len__(self):
        return len(self._nodes)

    def addNode(self, n):
        self._nodes.append(n)

    def adjacencyToGraph(self, adj):
        for n in adj:
            if len(n) != len(adj):
                raise ex.InvalidAdjacencyError()

        # start by creating the nodes
        adj = [[False if x == 0 else x for x in node] for node in adj]
        for (ind, el) in enumerate(adj):
            self.addNode(Node(ind))
        # set up connections between nodes now
        for (ind, el) in enumerate(self._nodes):
            for (ind_inner, el_inner) in enumerate(self._nodes):
                if adj[ind][ind_inner]:
                    el.add_connection([el_inner], adj[ind][ind_inner])

    def graphToAdjacency(self):
        adj = []
        for k in self.nodes:
            tmp = [False] * len(self)
            for l in k.connections:
                tmp[self.nodes.index(l.destination)] = l.metric
            adj.append(tmp)
        return adj

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        _edges = []
        [_edges.extend(x.connections) for x in self.nodes]
        return _edges

    def countEdges(self):
        return sum([len(a._connections) for a in self.nodes])

    def printGraphStats(self):
        print("Number of Nodes: {}\nNumber of Edges: {}\n"
              .format(len(self.nodes), self.countEdges()))

    def process(self):
        for k in self.edges:
            k.process()
        for k in self.nodes:
            k.process()


class Node(object):

    def __init__(self, UID):
        self._ID = UID
        self._connections = []
        self._rx = []
        self._tx = []
        self._routingTable = []

    def updateTableFromConnections(self):
        for item in self._connections:
            try:
                self._routingTable.index(item.destination)
            except ValueError:
                self._routingTable.append(RoutingTableEntry(item.destination,
                                                            item.destination,
                                                            item.metric,
                                                            None))

    def queuePacket(self, packet):
        self._tx.append(packet)

    def sendPacket(self, packet, edge):
        p=copy.copy(packet)
        for e in edge:
            p.nextHop = e.destination
            [item.addPacket(p) for item in edge]

    def receivePacket(self, packet):
        self._rx.append(packet)

    @property
    def connections(self):
        return self._connections

    def getID(self):
        return self._ID

    def add_connection(self, nodes, metric=0):
        for k in nodes:
            self._connections.append(Edge(k, metric))

    def process(self):
        pass


class Edge(object):

    def __init__(self, destination, metric):
        self._metric = metric
        self._destination = destination
        self._transit = []

    @property
    def destination(self):
        return self._destination

    @property
    def metric(self):
        return self._metric

    def addPacket(self, incomingPacket):
        self._transit.append(incomingPacket)
        incomingPacket.transitTime = self._metric

    def process(self):
        """
        Process the items waiting on the edge.
        There are no collisions and as such multiple
        packets can be sent over the Edge in a single timestep.

        Add packets to receiving node and remove from Edge
        if their transittime is up
        else keep them on the Edge and reduce remaining time by 1.
        """
        [self.handOff(item) if item.transitTime <= 1 else item.cycle()
         for item in self._transit]

    def handOff(self, packet):
        packet.nextHop.receivePacket(packet)
        self._transit.remove(packet)

    def get_Info(self):
        return (self._metric, self._destination)


class RoutingTableEntry(object):

    def __init__(self, destination,
                 nextHop, metric=None, seqNum=None):
        self.destination = destination
        self.nextHop = nextHop
        self.metric = metric
        self.SeqNum = seqNum

    def updateEntry(self, challengingEntry):
        if self.SeqNum < challengingEntry.SeqNum:
            return challengingEntry
        elif (self.SeqNum == challengingEntry.SeqNum and
              self.metric > challengingEntry.metric):
            return challengingEntry
        else:
            return self
