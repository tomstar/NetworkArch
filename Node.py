class Node(object):

    def __init__(self, UID):
        self._ID=UID

    def getID(self):
        return self._ID 

    def add_neighbour(self, n):
        print("Adding neighbour {0} to Node {1}".format(n.getID(), self._ID))
