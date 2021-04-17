import networkx as nx
import matplotlib
from tesseract import algorithms
import itertools
import logging

def is_clique(G):
    n = len(G.nodes())
    return (G.size() == n*(n-1)/2)

# Given a unordered chain of nodes, return the correct order
def sort_chain(G):
    endpoints = []
    for vertex in G.nodes():
        if G.degree(vertex) == 1:
            endpoints.append(vertex)
                
    paths = list(nx.shortest_simple_paths(G, endpoints[0],endpoints[1]))

    return paths[0]
    

# Get the minimal connected vertex cover
def get_mcvc(G):

    vertices = G.nodes()
    n = len(vertices)

    # If the graph is a clique, the mvc is simply n - 1 nodes
    if is_clique(G):
        
        return vertices[0:n-1]

    for i in range(1,n+1):
        # Compute all possible seqeunces of vertices
        vertex_cover_candidates = itertools.combinations(vertices, i)
        
        for candidate in vertex_cover_candidates:
            print("Trying candidate " + str(candidate))

            # First check if the candidate is connected
            H = nx.subgraph(G, candidate)

            if not nx.is_connected(H):
                print("Candidate " + str(candidate) + " is not connected. Skip")
                continue

            is_vertex_cover = True

            for edge in G.edges():
                if edge[0] not in candidate and edge[1] not in candidate:
                    is_vertex_cover = False
                    break

            if is_vertex_cover:
                return candidate

# We want to break down a pattern and its matching orders to a chain
def get_hierarchical_mcvc(G):
    hierarchical_mcvc = []

    H = G
    
    while True:
        mcvc = set(get_mcvc(H))

        if H.size() == len(mcvc) - 1:
            mcvc = sort_chain(H)
        
        mcvc_mapping = get_mcvc_mapping(H, mcvc)
        hierarchical_mcvc.insert(0,mcvc_mapping)

        H = nx.subgraph(G, mcvc)

        if H.size() == len(mcvc) - 1:
            break
    
    return hierarchical_mcvc

# Generate a mapping between a vertex in MCVC and its number of neighbours
def get_mcvc_mapping(G, mcvc):

    mapping = {}
    mapping = dict((el,dict()) for el in mcvc)

    for el in mapping:
        mapping[el]['exclusive'] = 0
        mapping[el]['common'] = dict()

    '''
    exclusive_neighbors = dict((el,0) for el in mcvc)
    common_neighbors = dict((el,dict()) for el in mcvc)
    '''

    for vertex in G.nodes():
        if vertex in mcvc:
            continue
        else:
            
            degree = G.degree(vertex)
            # If a node is not in mcvc and has a degree of 1
            # it has to be an exclusive neighour of a node in mcvc
            if degree == 1:
                key = list(G.edges(vertex))[0][1]

                mapping[key]['exclusive'] += 1

                print("Exclusive neighbor " + str(vertex) + " for " + str(key))

            # This node is a common neighbor for multiple mcvc nodes
            elif degree > 1:
                mcvc_vertices = [edge[1] for edge in G.edges(vertex)]

                if len(mcvc_vertices) == 2:
                    sharing_with = mcvc_vertices[1]
                else:
                    sharing_with = tuple(mcvc_vertices[1:])

                if mapping[mcvc_vertices[0]]['common'].get(sharing_with) == None:
                    mapping[mcvc_vertices[0]]['common'][sharing_with] = 1
                else:
                    mapping[mcvc_vertices[0]]['common'][sharing_with] += 1

    return mapping

PATTERN_PATH = "./test_patterns/pattern_3.adjlist"

G = nx.read_adjlist(PATTERN_PATH)

print("Edges imported:" + str(G.edges()))

num_nodes = len(G.nodes())

print("Number of nodes: " + str(num_nodes))

if not nx.is_connected(G):
    print("Error: the input pattern is not connected")
    exit(1)

mcvc = get_mcvc(G)
print("Minimal Connected Vertex Cover: " + str(mcvc))
                
exploration_plan = get_hierarchical_mcvc(G)

for i, plan in enumerate(exploration_plan):
    print("Plan number %d" %i)

    print("Matching order: %s" % str(plan.keys()))

    for j, vertex in enumerate(plan.keys()):
        print("%d (st/nd/rd/th) node (node %s in the input pattern) has %d exclusive neighbor" 
                % (j+1, vertex, plan[vertex]['exclusive']))
        
        sharing_with = plan[vertex]['common']
        for sharing_nodes in sharing_with:

            print("%d (st/nd/rd/th) node (node %s in the input pattern) shares %d neighbors with %s"
                 % (j+1, vertex, sharing_with[sharing_nodes], str(sharing_nodes)))