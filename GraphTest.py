#!/usr/bin/python3
__author__ = 'Thomas'

import unittest
from random import sample, randint
from statistics import mean, StatisticsError
import matplotlib as mpl

import Graph
import Packet
import Exceptions as customE


class GraphTest(unittest.TestCase):
    cases = []
    cases.append([[0, 1, 2, 1], [1, 0, 7, 3],
                  [3, 1, 0, 4], [5, 4, 2, 0]])
    cases.append([[0, 1, 0, 13], [1, 0, 1, 0],
                  [0, 1, 0, 0], [13, 0, 0, 0]])
    cases.append([[1, 1, 2, 1], [1, 1, 7, 3],
                  [3, 1, 1, 4], [5, 4, 2, 1]])
    cases.append([[False, 1, False, False], [1, False, 7, False],
                  [3, 1, False, 4], [False, False, 2, False]])
    cases.append([])
    cases.append([[1]])

    case100Nodes = [[randint(1, 1) * randint(1, 1) * randint(1, 1) if n != m
                     else False for n in range(100)]
                    for m in range(100)]
    cases.append(case100Nodes)

    def test_buildFromAdjacency(self):
        for adj in GraphTest.cases:
            g = Graph.Graph()
            g.adjacencyToGraph(adj)
            try:
                self.assertEqual(len(g.nodes[0].connections),
                                 (len(adj[0]) - adj[0].count(False)))
            except IndexError:
                pass

            self.assertEqual(adj, g.graphToAdjacency())
        with self.assertRaises(customE.InvalidAdjacencyError):
            g = Graph.Graph()
            g.adjacencyToGraph([[1, 9]])
        with self.assertRaises(customE.InvalidAdjacencyError):
            g = Graph.Graph()
            g.adjacencyToGraph([[3, 2, 1], [0, 0]])

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
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1],
                                  g.nodes[3], 2, 1))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1],
                                  g.nodes[3], 3, 1))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1],
                                  g.nodes[3], 1, 1))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1],
                                  g.nodes[3], 2, 2))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1],
                                  g.nodes[3], 3, 2))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1],
                                  g.nodes[3], 1, 2))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1],
                                  g.nodes[3], 2, 1))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1],
                                  g.nodes[3], 3, 1))
                tableentry.append(Graph.RoutingTableEntry(g.nodes[1],
                                  g.nodes[3], 1, 1))

                self.assertEqual(tableentry[2],
                                 tableentry[1].updateEntry(tableentry[2]))
                self.assertNotEqual(tableentry[2],
                                    tableentry[5].updateEntry(tableentry[2]))
                self.assertEqual(tableentry[4],
                                 tableentry[6].updateEntry(tableentry[4]))
                self.assertEqual(tableentry[1],
                                 tableentry[1].updateEntry(tableentry[1]))
                self.assertNotEqual(tableentry[2],
                                    tableentry[1].updateEntry(tableentry[4]))

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
                if node in [edge.destination for edge in node.connections]:
                    adjustment = 0
                else:
                    adjustment = 1
                self.assertEqual(len(node.connections) + adjustment,
                                 len(node._routingTable))

    def test_PacketPropagation(self):
        for adj in GraphTest.cases:
            g = Graph.Graph()
            g.adjacencyToGraph(adj)
            try:
                Packet.ControlPacket(dest=g.nodes[1],
                                     source=g.nodes[2], table=[])

            except IndexError:
                pass

    def test_transittime(self):
        for testcase in GraphTest.cases:
            g = Graph.Graph()
            g.adjacencyToGraph(testcase)
            for node in g.nodes:
                otherNodes = list(set([node]) ^ set(g.nodes))
                if any(otherNodes):
                    node.queuePacket(
                        Packet.ControlPacket(None,
                                             sample(otherNodes, 1),
                                             None))
            step = 0
            # while(g.process()):
            #     step = step + 1
            #     for e in g.edges:
            #         if (step) >= e.metric:
            #             # Edges with metric x have handed over all
            #             # packets after x timesteps
            #             # self.assertEqual(len(e._transit), 0)
            #             pass
            #         else:
            #             for packet in e._transit:
            #                 self.assertGreaterEqual(packet.transitTime, 1)

    def test_broadcastTable(self):
        for adj in self.cases:
            g = Graph.Graph()
            g.adjacencyToGraph(adj)
            g.updateRoutingTables()
            steps = 0
            while(g.process()):
                steps = steps + 1
                packets = sum([len(edge._transit) for edge in g.edges])
                packetSize = sum([sum([len(packet.RoutingTable) for packet in edge._transit])
                    for edge in g.edges])
                try:
                    avgSize = packetSize/packets
                except ZeroDivisionError:
                    avgSize = 0
                print("Step: {0} ({1} Packets\n"
                      "Average Packet Size: {2})".format(steps, packets, avgSize))

            tableLength = [len(node._routingTable) for node in g.nodes]
            try:
                avgTableLength = mean(tableLength)
                sumTableLength = sum(tableLength)
            except StatisticsError:
                tableLength = 0
                sumTableLength = 0

            print("Steps: {0}\nAverage Table: {1}"
                  .format(steps, avgTableLength))
            self.assertEqual(len(g.nodes) * len(g.nodes),
                             sumTableLength)


if __name__ == '__main__':
    unittest.main()
