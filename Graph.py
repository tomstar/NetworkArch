class Graph(object):

    def __init__(self):
        self._nodes=[]

    def addNode(self, n):
        self._nodes.append(n)
        print('Node {} added to Graph'.format(n.getID()))


class Node(object):

    def __init__(self, UID):
        self._ID=UID
        self._connections=[]

    def getID(self):
        return self._ID

    def add_connection(self, n, metric=0):
        self._connections.append(Edge(n, metric))
        print('Adding connection to Node {0} with metric {1}'.format(n.getID(), metric)) 


class Edge(object):
    
    def __init__(self, destination, metric):
        self._metric=metric
        self._destination=destination

    def get_Info(self):
        return (self._metric, self._destination)
