#!/usr/bin/python3
__author__ = 'Thomas'

import unittest

import Graph


class GraphTest(unittest.TestCase):
    def test_buildFromAdjacency(self):
        adj = [[False, 1, False, False], [1, False, 7, False],
               [3, 1, False, 4], [False, False, 2, False]]
        g = Graph.Graph()
        g.adjacencyToGraph(adj)

        self.assertEqual(len(g), 4)
        self.assertEqual(len(g.nodes[0].connections),
                         (len(adj[0]) - adj[0].count(False)))
        self.assertEqual(g.nodes[2].connections[-1].destination, g.nodes[3])
        self.assertEqual(adj, g.graphToAdjacency())

    def test_addMultiple(self):
        l = []
        for k in [1, 2, 3, 4]:
            l.append(Graph.Node(k))
        for k in l:
            k.add_connection(l)

        self.assertEqual(len(l[2].connections), 4)


if __name__ == '__main__':
    unittest.main()
