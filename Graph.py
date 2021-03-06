#!/usr/bin/python3
import pickle
import copy
from random import shuffle

import Exceptions as ex
import Packet


class Graph(set):
    """
    Graph class containing Nodes and Edges.

    Edges can be unidirectional with different weight for the directions.
    """
    def __init__(self):
        super(Graph, self).__init__(self)
        self._nodes = []

    def store(self, filename):
        """
        Store graph as pickle
        """
        pickle.dump(self, open(filename, 'bw'))

    def updateRoutingTables(self):
        """
        update 1-hop routing table entries
        """
        for node in self.nodes:
            node.updateTableFromConnections()

    def __len__(self):
        return len(self._nodes)

    def addNode(self, n):
        """
        add node to graph
        """
        self._nodes.append(n)

    def checkConnectivity(self, adj):
        adj = self.adjToBool(adj)
        initial = adj[0]
        previous = initial
        current = (False, False)
        while (set(previous)^set(current)):
            for val, el in enumerate(current):
                if val:
                    current = current or previous[el]
                    previous[el] = current[el]
        return current

    def adjToBool(self, adj):
        return [[bool(m) for m in n] for n in adj]

    def adjacencyToGraph(self, adj):
        """
        add nodes and connections to a graph according to
        a NxN adjacency matrix

        adj := list of N-lists (each length N)
               connection represented by value => 1 (metric)
               no connection between nodes represented by value False or 0
        """
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
        """
        return a graphs adjacency matrix
        returned object is list of N-lists (each length N)
        """
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
        """
        return all edges in the graph
        edges is union of all outgoing connections of all nodes
        """
        _edges = []
        [_edges.extend(x.connections) for x in self.nodes]
        return _edges

    def countEdges(self):
        return sum([len(a._connections) for a in self.nodes])

    def printGraphStats(self):
        print("Number of Nodes: {}\nNumber of Edges: {}\n"
              .format(len(self.nodes), self.countEdges()))

    def process(self, randomOrder=True):
        """
        execute processing steps for all nodes and edges
        in random order
        """
        # processed: a packet process has taken place
        processed = False
        objects = copy.copy(self.edges)
        objects.extend(self.nodes)
        if randomOrder:
            shuffle(objects)
        for k in objects:
            processed = k.process() or processed
        return processed


class Node(object):

    def __init__(self, UID):
        self._ID = UID
        self._connections = []
        self._rx = []
        self._tx = []
        self._routingTable = {}
        self._tableUpdates = {}

    def updateTableFromConnections(self):
        """
        add entries to routing table if they don't already exist
        """
        update = False
        for item in self.connections:
            try:
                self._routingTable[item.destination.ID]
            except KeyError:
                self._routingTable[item.destination.ID] = RoutingTableEntry(
                    item.destination,
                    item.destination,
                    item.metric,
                    None
                )
                update = True
            else:
                self._routingTable[item.destination.ID].updateEntry(
                    RoutingTableEntry(
                        item.destination,
                        item.destination,
                        item.metric,
                        None
                    )
                )
                update = True
        # if not explicitly set: loopback with metric 0
        try:
            self._routingTable[self.ID]
        except KeyError:
            self._routingTable[self.ID] = RoutingTableEntry(
                self,
                self,
                0,
                None
            )
        if update:
            self._tableUpdates = self._routingTable
            self.broadcastTablechange()

    def updateTableFromPacket(self, packet):
        update = False
        entries = list(packet.RoutingTable.values())
        for entry in entries:
            try:
                self._routingTable[entry.destination.ID]
            except KeyError:
                try:
                    self._routingTable[packet.lastNode.ID]
                except KeyError:
                    pass
                else:
                    newEntry = RoutingTableEntry(
                        entry.destination,
                        packet.lastNode,
                        self._routingTable[packet.lastNode.ID].metric + entry.metric,
                        None)
                    self._routingTable[entry.destination.ID] = newEntry
                    self._tableUpdates[entry.destination.ID] = newEntry
                    update = True
            else:
                try:
                    self._routingTable[packet.lastNode.ID]
                except KeyError:
                    pass
                else:
                    if ((self._routingTable[packet.lastNode.ID].metric + entry.metric) < (self._routingTable[entry.destination.ID].metric)):
                        newEntry = RoutingTableEntry(
                            entry.destination,
                            packet.lastNode,
                            self._routingTable[packet.lastNode.ID].metric + entry.metric,
                            None)
                        self._routingTable[entry.destination.ID] = newEntry
                        self._tableUpdates[entry.destination.ID] = newEntry
                        update = True
        return update

    def broadcastTablechange(self):
        packet = Packet.ControlPacket(
            self,
            self,
            copy.copy(self._tableUpdates)
            )
        self.queuePacket(packet)
        self._tableUpdates = {}

    def queuePacket(self, packet):
        """
        add a packet to the transmission queue
        """
        self._tx.append(packet)

    def sendPacket(self, packet, edge):
        """
        send a copy of the packet on all edges in 'edge'
        """
        packet.lastNode = self
        for e in edge:
            p = copy.copy(packet)
            p.nextHop = e.destination
            e.addPacket(p)

    def receivePacket(self, packet):
        """
        add a packet to the receiver queue
        executed by an edge transmission process
        """
        self._rx.append(packet)

    @property
    def connections(self):
        return self._connections

    @property
    def ID(self):
        return self._ID

    def add_connection(self, nodes, metric=0):
        for k in nodes:
            self._connections.append(Edge(k, metric))

    def process(self):
        """
        process operations for the node
        """
        processed = False
        tableUpdate = False
        for received in self._rx:
            if received.destination == self:
                pass
            else:
                tableUpdate = self.updateTableFromPacket(received) or tableUpdate
        if tableUpdate:
            self.broadcastTablechange()

        for packet in self._tx:
            self.sendPacket(packet, self.connections)
            self._tx.remove(packet)
            processed = True

        return processed


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
        """
        add packet to the edge's transit list
        set the remaining transit time to be proportional to
        the edge's metric
        """
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
        processed = len(self._transit) > 0
        [self.handOff(item) if item.transitTime <= 1
         else item.cycle()
         for item in self._transit]
        return processed

    def handOff(self, packet):
        """
        Hand a packet over to a receiving node.
        """
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
