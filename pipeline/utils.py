from __future__ import absolute_import


ITERATED = 1
NEW = 0
ITERATING = -1


def has_circle(graph):
    # init marks
    marks = {}
    for node in graph:
        # marks as not iterated
        marks[node] = NEW

    # dfs every node
    for cur_node in graph:
        trace = [cur_node]
        for node in graph[cur_node]:
            if marks[node] == ITERATED:
                continue
            trace.append(node)
            # return immediately when circle be detected
            if _has_circle(graph, node, marks, trace):
                return True, trace
            trace.pop()
        # mark as iterated
        marks[cur_node] = ITERATED

    return False, []


def _has_circle(graph, cur_node, marks, trace):
    # detect circle when iterate to a node which been marked as -1
    if marks[cur_node] == ITERATING:
        return True
    # mark as iterating
    marks[cur_node] = ITERATING
    # dfs
    for node in graph[cur_node]:
        # return immediately when circle be detected
        trace.append(node)
        if _has_circle(graph, node, marks, trace):
            return True
        trace.pop()
    # mark as iterated
    marks[cur_node] = ITERATED

    return False
