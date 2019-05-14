# -*- coding: utf-8 -*-


class Graph(object):
    def __init__(self, nodes, flows):
        self.nodes = nodes
        self.flows = flows
        self.path = []
        self.last_visited_node = ''

    def has_cycle(self):
        self.path = []
        for node in self.nodes:
            if self.visit(node):
                return True
        return False

    def visit(self, node):
        self.path.append(node)
        target_nodes = [flow[1] for flow in self.flows if flow[0] == node]
        for target in target_nodes:
            if target in self.path:
                self.last_visited_node = target
                return True
            if self.visit(target):
                return True
        self.path.remove(node)
        return False

    def get_cycle(self):
        if self.has_cycle():
            index = self.path.index(self.last_visited_node)
            cycle = self.path[index:]
            cycle.append(self.last_visited_node)
            return cycle
        return []


if __name__ == '__main__':
    graph1 = Graph([1, 2, 3, 4], [[1, 2], [2, 3], [3, 4]])
    print 'graph1 has cycle %s' % graph1.has_cycle()
    graph2 = Graph([1, 2, 3, 4], [[1, 2], [2, 3], [3, 4], [4, 1]])
    print 'graph2 has cycle %s' % graph2.has_cycle()
    print 'graph2 cycle is %s' % graph2.get_cycle()
    graph3 = Graph([1, 2, 3, 4], [[1, 2], [2, 3], [3, 4], [4, 2]])
    print 'graph3 has cycle %s' % graph3.has_cycle()
    print 'graph3 cycle is %s' % graph3.get_cycle()
