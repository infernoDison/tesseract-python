import copy
import logging
import math

from tesseract import canonical

import networkx as nx


class Algorithm:
    def __init__(self, out, max=math.inf):
        self.max = max
        self.num_filters = 0
        self.num_found = 0
        self.out = out
        self.log = logging.getLogger('ALGO')

    def filter(self, e, G, last_v):
        self._inc_filter()
        return True

    def process(self, e, G):
        self._inc_found()
        self.out.found(e, G)

    def _inc_filter(self):
        self.num_filters += 1

    def _inc_found(self):
        self.num_found += 1

    def _inc_found_x(self, x):
        self.num_found += x

    def reset_stats(self):
        self.num_filters = 0
        self.num_found = 0


class CliqueFinding(Algorithm):
    def __init__(self, out, max=math.inf):
        super().__init__(out, max)

    def filter(self, e, G, last_v):
        super()._inc_filter()
        # This is the fastest implementation
        v = last_v if last_v is not None else e[-1]
        for u in e:
            if u != v and not G.has_edge(u, v):
                return False
        return True

        # Another implementation (surprisingly fast)
        """
        count = 0
        for i, u in enumerate(e):
            for v in e[i:]:
                if G.has_edge(u, v):
                    count +=1
        return count == int(len(e) * (len(e) - 1) / 2)
        """

        # And yet another (slower)
        """
        v = last_v if last_v is not None else e[-1]
        edges_added_with_expansion = [edge for edge in G.edges(v) if edge[1] in e]  # for directed, need edges going to v, not from v
        return len(edges_added_with_expansion) == len(e) - 1
        """

    def process(self, e, G):
        if len(e) >= 3:
            self._inc_found()
            self.out.found(e, G, tpe='%d-clique' % len(e))


class CycleFinding(Algorithm):
    def __init__(self, out, max=math.inf):
        super().__init__(out, max)

    def filter(self, e, G, last_v):
        super()._inc_filter()
        return True

    def process(self, e, G):
        if len(e) > 2 and CycleFinding._is_cycle(e, G):
            self._inc_found()
            self.out.found(e, G, tpe='%d-cycle' % len(e))

    @staticmethod
    def _is_cycle(e, G):
        cycles = []
        path = []

        def visit(v):
            path.append(v)
            for u in [edge[1] for edge in G.edges(v) if edge[1] in e]:
                if u == path[0]:
                    cycles.append(copy.deepcopy(path))
                elif u not in path:
                    visit(u)
            path.remove(v)

        visit(e[0])

        for cycle in cycles:
            if len(cycle) == len(e):
                return True

'''
class ExamplePatternFinding(Algorithm):
    def __init__(self, out, max=math.inf):
        super().__init__(out, 4)

    def filter(self, e, G, last_v):
        super()._inc_filter()
        return True

    def process(self, e, G):
        
        if len(e) == 4:
            ret = ExamplePatternFinding._is_cycle(e, G)
            if ret == 1:
                self._inc_found()
            elif ret == 2:
                self._inc_found_x(5)
            else:
                return False
            self.out.found(e, G, tpe='%d-cycle' % len(e))

    @staticmethod
    def _is_cycle(e, G):
        count_2 = 0
        count_3 = 0
        for i in range(4):
            curr_count = len([edge[1] for edge in G.edges(e[i]) if edge[1] in e])
            if curr_count >= 2:
                count_2 += 1
            if curr_count >= 3:
                count_3 += 1
        if count_2 == 4 and count_3 == 2:
            return 1
        elif count_2 == 4 and count_3 == 4:
            return 2
        return 0

'''
class ExamplePatternFinding(Algorithm):
    def __init__(self, out, max=math.inf):
        super().__init__(out, 3)

    def filter(self, e, G, last_v):
        super()._inc_filter()
        v = last_v if last_v is not None else e[-1]
        for u in e:
            if u != v and not G.has_edge(u, v):
                return False
        return True

    def process(self, e, G):
        if len(e) == 2:
            neighbor = nx.common_neighbors(G, e[0], e[1])
            x = sum(1 for _ in neighbor)
            if x >= 2:
                #print(list(neighbor))
                self._inc_found_x(x * (x-1) / 2)
                self.out.found(e, G, tpe='%d-found' % len(e))
                return True
        elif len(e) == 3:
            has_match = False
            neighbor = nx.common_neighbors(G, e[0], e[-1])
            x = sum(1 for _ in neighbor)
            if x >= 2:
                #print(list(neighbor))
                self._inc_found_x(x-1)
                self.out.found(e, G, tpe='%d-found' % len(e))
                has_match = True
            neighbor = nx.common_neighbors(G, e[1], e[-1])
            x = sum(1 for _ in neighbor)
            if x >= 2:
                #print(list(neighbor))
                self._inc_found_x(x-1)
                self.out.found(e, G, tpe='%d-found' % len(e))
                has_match = True
            return has_match
        return False


class ExampleTree(Algorithm):
    def __init__(self, out, max):
        super().__init__(out, 5 if max > 5 else max)

    def filter(self, e, G, last_v):
        super()._inc_filter()
        if len(e) < self.max:
            return True
        elif len(e) == self.max:
            for u in e:
                neighbors = [edge[1] for edge in G.edges(u) if edge[1] in e]
                if len(neighbors) == 3:
                    w = [v for v in e if v != u and v not in neighbors][0]  # non neighbor
                    for v in neighbors:
                        if G.has_edge(w, v):
                            return True
                elif len(neighbors) == 4:
                    for i, v in enumerate(neighbors):
                        for w in neighbors[i:]:
                            if G.has_edge(w, v):
                                return True
            return False
        return False

    def process(self, e, G):
        if len(e) == self.max:
            self._inc_found()
            self.out.found(e, G, tpe='tree')