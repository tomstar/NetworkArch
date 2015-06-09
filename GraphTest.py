#!/usr/bin/python3
__author__ = 'Thomas'

import unittest

import Graph
import Packet


class GraphTest(unittest.TestCase):
    cases = []
    cases.append([[1, 1, 2, 1], [1, 1, 7, 3],
                  [3, 1, 1, 4], [5, 4, 2, 1]])
    cases.append([[False, 1, False, False], [1, False, 7, False],
                  [3, 1, False, 4], [False, False, 2, False]])
    cases.append([])
    cases.append([[1]])
    def test_buildFromAdjacency(self):
        for adj in GraphTest.cases:
            g = Graph.Graph()
            g.adjacencyToGraph(adj)
            try:
                self.assertEqual(len(g.nodes[0].connections),
                                 (len(adj[0]) - adj[0].count(False)))
                self.assertEqual(g.nodes[2].connections[-1].destination, g.nodes[3])

            except IndexError:
                pass

            self.assertEqual(adj, g.graphToAdjacency())

    def test_addMultiple(self):
        l = []
        for k in [1, 2, 3, 4]:
            l.append(Graph.Node(k))
        for k in l:
            k.add_connection(l)

        self.assertEqual(len(l[2].connections), 4)
    
    def test_tableComparison(self):
        for adj in GraphTest.cases:
            g = Graph.Graph()
            g.adjacencyToGraph(adj)
            tableentry = []
            try:
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1], g.nodes[3], 2, 1))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1], g.nodes[3], 3, 1))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1], g.nodes[3], 1, 1))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1], g.nodes[3], 2, 2))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1], g.nodes[3], 3, 2))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1], g.nodes[3], 1, 2))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1], g.nodes[3], 2, 1))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1], g.nodes[3], 3, 1))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1], g.nodes[3], 1, 1))

                self.assertEqual(tableentry[2], tableentry[1].updateEntry(tableentry[2]))
                self.assertNotEqual(tableentry[2], tableentry[5].updateEntry(tableentry[2]))
                self.assertEqual(tableentry[4], tableentry[6].updateEntry(tableentry[4]))
                self.assertEqual(tableentry[1], tableentry[1].updateEntry(tableentry[1]))
                self.assertNotEqual(tableentry[2], tableentry[1].updateEntry(tableentry[4]))

            except IndexError:
                pass

    def test_edgesInGraph(self):
        for adj in GraphTest.cases:
            g = Graph.Graph()
            g.adjacencyToGraph(adj)
            self.assertEqual(g.countEdges(), len(g.edges))

    def test_buildTableFromConnections(self):
        for adj in GraphTest.cases:
            g = Graph.Graph()
            g.adjacencyToGraph(adj)
            g.updateRoutingTables()
            for node in g.nodes:
                self.assertEqual(len(node.connections), len(node._routingTable))



    def test_PacketPropagation(self):
        for adj in GraphTest.cases:
            g = Graph.Graph()
            g.adjacencyToGraph(adj)
            try:
                p1 = Packet.ControlPacket(dest=g.nodes[1], source=g.nodes[2], table=[])

            except IndexError:
                pass


if __name__ == '__main__':
    unittest.main()
