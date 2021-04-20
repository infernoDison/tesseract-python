import logging

from tesseract import canonical, graph


LOG = logging.getLogger('MINE')


def forwards_explore(G, alg, c):
    if len(c) == alg.max:
        return
    else:
        V = set(graph.neighborhood(c, G))
        for v in V:
            if v not in c:
                if canonical.canonical(c, v, G):
                    c.append(v)
                    LOG.debug('%s %s' %(str(c), 'F'))
                    if alg.filter(c, G, v):
                        alg.process(c, G)
                        forwards_explore(G, alg, c)
                    c.pop()
                else:
                    LOG.debug('%s %s' %(str(c), 'R'))


def forwards_explore_all(G, f):
    for v in G.nodes:
        forwards_explore(G, f, [v])


def backwards_explore(G, alg, c, last_v=None):
    if not canonical.canonical_r2_all(c, G):
        LOG.debug('%s %s' %(str(c), 'R2'))
        return
    elif not canonical.canonical_r1_all(c):
        LOG.debug('%s %s' %(str(c), 'R1'))
    else:
        LOG.debug('%s %s' %(str(c), 'F'))
        if alg.filter(c, G, last_v):
            alg.process(c, G)
        else:
            return

    if len(c) > alg.max:
        return
    else:
        V = set(filter(lambda v: last_v is None or True, graph.neighborhood(c, G)))
        for v in V:
            if v not in c:
                for i in range(0, len(c) + 1):
                    c.insert(i, v)
                    if graph.is_connected(v, c, G):
                        backwards_explore(G, alg, c, v)
                    c.pop(i)


def backwards_explore_update(G, alg, edge, add_to_graph=True):
    if len(edge) != 2:
        return
    G.add_edge(edge[0], edge[1])
    backwards_explore(G, alg, edge)
    backwards_explore(G, alg, [edge[1], edge[0]])
    if not add_to_graph:
        G.remove_edge(edge[0], edge[1])


def middleout_explore(G, alg, c, ignore=[], mo=True, left=False, right=False):

    # c: start as a single edge e.g. (0,1) and every recursion adds a 
    # neighbour to it
    # print(c)
    # Reaches the base case when the maximum size clique is found
    print('middleout_explore with c: ', c, mo, left, right)

    alg.process(c, G, mo, left, right)

    if mo and len(c) == alg.max:
        #print('stop by max of ', alg.max)
        return
    elif not mo and len(c) == alg.max + 1:
        #print('stop by max of ', alg.max, '+1')
        return
    else:
        # Get all the connected neighbour vertex of the edge
        #V = set(G.neighbors(c[-1]))
        if mo:
            V = set(graph.neighborhood(c, G))
        else:
            V_ori = set(graph.neighborhood(c[2:], G))
            V = set(graph.neighborhood(c[2:], G))
            V_left = graph.neighborhood(c[0], G)
            V_right = graph.neighborhood(c[1], G)
            if left:
                V.update(V_left)
            if right:
                V.update(V_right)
        #print(G.edges(c))
        #print(V)
        #input("Press Enter to continue...2")
        for v in V:
            # If the edge c does not contain the vertex
            if v not in c:
                if canonical.canonical_r2(c, v, G, ignore=ignore):
                    #print(v)
                    #input("Press Enter to continue...3")
                    c.append(v)
                    LOG.debug('%s %s' %(str(c), 'F'))

                    # Check if the neighor is connected to any sides of the edge
                    if alg.filter(c, G, v):
                        # For cliques, we find a n-d clique
                        #alg.process(c, G)

                        # Keep going to find a larger clique
                        new_left = False
                        new_right = False
                        if not mo and v in V_ori:
                            new_left = left
                            new_right = right
                            if v in V_left:
                                new_left = True
                            if v in V_right:
                                new_right = True
                        elif not mo:
                            if v in V_left and v in V_right:
                                new_left = left
                                new_right = right
                            else:
                                if v in V_left:
                                    new_left = True
                                if v in V_right:
                                    new_right = True

                        middleout_explore(G, alg, c, ignore=ignore, mo=mo, left=new_left, right=new_right)
                    c.pop()
                else:
                    LOG.debug('%s %s' %(str(c), 'R'))


def middleout_explore_update(G, alg, edge, add_to_graph=True):
    print("Add edge:" + str(edge))
    #input("Press Enter to continue...1")
    if len(edge) != 2:
        return
    G.add_edge(edge[0], edge[1])

    # I think the "ignore" here prevent redundant exploration

    # 1st time call: try to use the new edge as a part of the matching order
    middleout_explore(G, alg, edge, ignore=[edge[1]], mo=True)

    # 2nd time call: extend the edge in a different direction as the matching order
    #if alg.matching_order_size > 2:
    middleout_explore(G, alg, edge, ignore=[edge[1]], mo=False, left=True, right=True)

    if not add_to_graph:
        G.remove_edge(edge[0], edge[1])
