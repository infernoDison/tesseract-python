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


def middleout_explore(G, alg, c, ignore=[]):

    # c: start as a single edge e.g. (0,1) and every recursion adds a 
    # neighbour to it

    # Reaches the base case when the maximum size clique is found
    if len(c) > alg.max:
        return
    else:
        alg.process(c, G)
        # Get all the connected neighbour vertex of the edge
        V = set(graph.neighborhood(c, G))
        for v in V:
            #print(c)
            #print(G.edges(c))
            #print(v)
            #print(V)
            #input("Press Enter to continue...2")
            # If the edge c does not contain the vertex
            if v not in c:
                if canonical.canonical_r2(c, v, G, ignore=ignore):
                    c.append(v)
                    LOG.debug('%s %s' %(str(c), 'F'))

                    # Check if the neighor is connected to any sides of the edge
                    if alg.filter(c, G, v):

                        # For cliques, we find a n-d clique
                        #alg.process(c, G)

                        # Keep going to find a larger clique
                        middleout_explore(G, alg, c, ignore=ignore)
                    c.pop()
                else:
                    LOG.debug('%s %s' %(str(c), 'R'))


def middleout_explore_update(G, alg, edge, add_to_graph=True):
    #print(edge)
    #print(len(edge))
    #input("Press Enter to continue...1")
    if len(edge) != 2:
        return
    G.add_edge(edge[0], edge[1])

    # I think the "ignore" here prevent redundant exploration
    middleout_explore(G, alg, edge, ignore=[edge[1]])
    if not add_to_graph:
        G.remove_edge(edge[0], edge[1])
