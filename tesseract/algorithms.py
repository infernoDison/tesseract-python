import copy
import logging
import math
import itertools

from tesseract import canonical

import networkx as nx

import parse_pattern 


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


class ExamplePatternFindingBaseline(Algorithm):
    def __init__(self, out, max=math.inf):
        super().__init__(out, 4)

    def filter(self, e, G, last_v):
        super()._inc_filter()
        return True

    def process(self, e, G):
        
        if len(e) == 4:
            ret = ExamplePatternFindingBaseline._is_cycle(e, G)
            if ret == 1:
                self._inc_found()
                self.out.found(e, G, tpe='%d-cycle' % len(e))
            elif ret == 2:
                self._inc_found_x(5)

                # 5 duplicates
                for i in range(5):
                    self.out.found(e, G, tpe='%d-cycle' % len(e))
                
            else:
                return False
            

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

            neighbor_cp = neighbor

            # Get all pairs of common neighbors
            rest_patterns = list(itertools.combinations(nx.common_neighbors(G, e[0], e[1]), 2))

            x = sum(1 for _ in neighbor)
            if x >= 2:
                #print(list(neighbor))
                self._inc_found_x(x * (x-1) / 2)

                for pair in rest_patterns:
                    full_pattern = e + list(pair)
                    self.out.found(full_pattern, G, tpe='%d-found' % len(full_pattern))
                
                return True
        elif len(e) == 3:
            has_match = False
            neighbor = nx.common_neighbors(G, e[0], e[-1])

            # Get all pairs of common neighbors
            #rest_patterns = list(itertools.combinations(nx.common_neighbors(G, e[0], e[-1]), 2))
            '''
            x = sum(1 for _ in neighbor)
            if x >= 2:
                #print(list(neighbor))
                self._inc_found_x(x-1)
                    
                    #print(full_pattern)
                    self.out.found(full_pattern, G, tpe='%d-found' % len(full_pattern))
                
                #self.out.found(e, G, tpe='%d-found' % len(e))
                has_match = True
            '''

            for node in neighbor:
                if node != e[1]:
                    self._inc_found()
                    full_pattern = e + [node]
                    self.out.found(full_pattern, G, tpe='%d-found' % len(full_pattern))
                    has_match = True
            
            neighbor = nx.common_neighbors(G, e[1], e[-1])

            # Get all pairs of common neighbors
            #rest_patterns = list(itertools.combinations(nx.common_neighbors(G, e[1], e[-1]), 2))
            
            '''
            x = sum(1 for _ in neighbor)
            if x >= 2:
                #print(list(neighbor))
                self._inc_found_x(x-1)

                for pair in rest_patterns:
                    full_pattern = e
                    # We want the one contains e[1] already
                    if e[1] not in pair:
                        continue
                    else:
                        full_pattern += pair[0] if pair[0] != e[1] else pair[1]
                    
                    #print(full_pattern)
                    self.out.found(full_pattern, G, tpe='%d-found' % len(full_pattern))
                #self.out.found(e, G, tpe='%d-found' % len(e))
                has_match = True
            '''
            for node in neighbor:
                if node != e[0]:
                    self._inc_found()
                    full_pattern = e + [node]
                    self.out.found(full_pattern, G, tpe='%d-found' % len(full_pattern))
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

    
class PeregrinePatternMatching(Algorithm):
    def __init__(self, out, pattern_path, max=math.inf):

        P = nx.read_adjlist(pattern_path)
        
        self.exclusive_neighbors = {}
        self.common_neighbors = {}

        # TODO: For the current test patterns, all matching orders are simple
        plan = parse_pattern.get_hierarchical_mcvc(P)[0]

        self.matching_order_size = len(plan.keys())

        # The middle out terminates when we have more nodes than matching_order_size
        super().__init__(out, self.matching_order_size)

        for vertex in plan.keys():

            if plan[vertex]['exclusive'] != 0:
                self.exclusive_neighbors[vertex] = plan[vertex]['exclusive']
        
            sharing_with = plan[vertex]['common']

            if sharing_with:
                for sharing_nodes in sharing_with:
                    self.common_neighbors[vertex] = sharing_with

        self.max = self.matching_order_size
        self.print()

    def print(self):
        print(self.matching_order_size)
        print(self.exclusive_neighbors)
        print(self.common_neighbors)

    '''
    filter is designed to find the matching order only
    '''
    def filter(self, e, G, last_v):
        super()._inc_filter()

        #if len(e) > self.matching_order_size:
        #    return False

        return True

    def process(self,e,G,mo,left,right):

        my_mos = []
        nodes_removed = []

        if mo:
   
            if len(e) != self.matching_order_size:
                return False
            else:
                #print('mo', e)  
                my_mos.append(e)
        else:
            if len(e) != self.matching_order_size + 1:
                return False
            if left:
                t = e[:1] + e[2:]
                if len(t) > 2:
                    H = G.subgraph(t)
                    new_e = parse_pattern.sort_chain(H)
                    my_mos.append(new_e)
                    nodes_removed.append(e[1])

                    my_mos.append(list(reversed(new_e)))
                    nodes_removed.append(e[1])
                else:  
                #print('mo', e[:1] + e[2:])
                    my_mos.append(e[:1] + e[2:])
                    nodes_removed.append(e[1])
            if right:
                t = e[1:]
                print("t" + str(t))
                if len(t) > 2:
                    H = G.subgraph(t)
                    print(H)
                    new_e = parse_pattern.sort_chain(H)
                    my_mos.append(new_e)
                    nodes_removed.append(e[0])

                    my_mos.append(list(reversed(new_e)))
                    nodes_removed.append(e[0])
                else:  
                #print('mo', e[:1] + e[2:])
                    my_mos.append(e[1:])
                    nodes_removed.append(e[0])


        print(my_mos)
        print(nodes_removed)


        for i, my_mo in enumerate(my_mos):
            print(my_mo)

            # Here we have a valid matching order
            # We need to check if we can construct the pattern from it

            # First, go over the exclusive neighbors
            total_en_combinations = 1
            
            premature_exit = False
            for index in self.exclusive_neighbors:

                if self.exclusive_neighbors[index] == 0:
                    continue

                # Corresponding node in the matching order
                cur_vertex = my_mo[index]
                
                # Neighbors of the current node in the matching order
                neighbors = G.neighbors(cur_vertex)

                en = []
                for neighbor in neighbors:
                    if neighbor not in my_mo:
                        en.append(neighbor)

                num_en = len(en)
                print("en:" + str(en))
                en_requirement = self.exclusive_neighbors[index]

                if num_en < en_requirement:
                    print("Too few exclusive neighbors for the %d th node " % (index))
                    premature_exit = True
                    break
                
                print("Exclusive neighbors for the %d th node: %d" % (index, num_en))

                # Compute how many combinations (aka matches) we can get for the exclusive neighbors
                en_combination = parse_pattern.nCk(num_en, en_requirement)
                total_en_combinations = total_en_combinations * en_combination
            
            cn_combinations_list = []
            no_new_match = True

            # The exclusive neighbor constraints have already failed
            # No need to check the common neighbors
            if premature_exit:
                continue
            else:
                premature_exit = False

            for index in self.common_neighbors:
                
                if premature_exit:
                    # One of the common_neighbor constraint has failed
                    break

                # Corresponding node in the matching order
                cur_vertex = my_mo[index]

                # A node will share common neighbors with different sets of other nodes
                # in the matching order
                for sharing_with in self.common_neighbors[index]:
                    #input("Press enter to continue:")
        
                    if type(sharing_with) is int:
                        cn = set(nx.common_neighbors(G, cur_vertex, my_mo[sharing_with]))
                    else:
                        cn = None
                        # Iterate through others nodes in each set
                        for node_index in sharing_with:
                            node = my_mo[node_index]
                            shared_neighbors = nx.common_neighbors(G, cur_vertex, node)

                            if not cn:
                                cn = set(shared_neighbors)
                            else:
                                cn = cn.intersection(shared_neighbors)

                            # Since we only store non-zero common neighbors, we can exit if 
                            # none is found
                            if len(cn) == 0:
                                break 
                    
                    # discard the common neighbors that are from the mo
                    for node in my_mo:
                        cn.discard(node)

                    print(cn)
                    num_cn = len(cn)
                    cn_requirement = self.common_neighbors[index][sharing_with]
                    # One of the common neighbor requirement is not satisfied
                    if num_cn < cn_requirement:
                        premature_exit = True
                        break 
                        
                    print("Common-neighbor constraint for %d th node with nodes %s is satisfied " % 
                        (index,str(sharing_with)))

                    # If the newly introduced edge does not belong to any pattern found
                    cn_combination = parse_pattern.nCk(num_cn,cn_requirement)
                    if mo:
                        print("This is a matching order")
                        print(cn_combination)
                        pass
                    elif nodes_removed[i] not in cn:
                        print("Not a new match")
                        cn_combination = 0
                    elif num_cn == cn_requirement:
                        cn_combination = 1
                    elif num_cn > cn_requirement:
                        cn_combination = num_cn - 1

                    if cn_combination > 0:
                        no_new_match = False
                        cn_combinations_list.append(cn_combination)

            print(cn_combinations_list)
            total_cn_combinations = 1
            if no_new_match or premature_exit:
                total_cn_combinations = 0
            else:
                for el in cn_combinations_list:
                    total_cn_combinations *= el

            total_matches = total_en_combinations * total_cn_combinations 

            if total_matches > 0:               
                super()._inc_found_x(total_matches)
                print("We found %d matches with matching order %s" % (total_matches, str(my_mo)))
        
