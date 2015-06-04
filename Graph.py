#!/usr/bin/python3
import pickle


class Graph(set):

    def __init__(self):
        super(Graph, self).__init__(self)
        self._nodes = []

    def store(self, filename):
        pickle.dump(self, open(filename, 'bw'))

    def __len__(self):
        return len(self._nodes)

    def addNode(self, n):
        self._nodes.append(n)
        print('Node {} added to Graph'.format(n.getID()))

    def adjacencyToGraph(self, adj):
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

    def countEdges(self):
        return sum([len(a._connections) for a in self.nodes])

    def printGraphStats(self):
        print("Number of Nodes: {}\nNumber of Edges: {}\n"
              .format(len(self.nodes), self.countEdges()))


class Node(object):

    def __init__(self, UID):
        self._ID = UID
        self._connections = []
        self._rx = []
        self._tx = []

    def updateTable(self):
        pass

    @property
    def connections(self):
        return self._connections

    def getID(self):
        return self._ID

    def add_connection(self, nodes, metric=0):
        for k in nodes:
            self._connections.append(Edge(k, metric))


class Edge(object):

    def __init__(self, destination, metric):
        self._metric = metric
        self._destination = destination

    @property
    def destination(self):
        return self._destination

    @property
    def metric(self):
        return self._metric

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

