import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from networkx.algorithms import approximation
import random
from utility import Stats


#takes dictionary of links and facilities, plots topology graph, useless for huge graphs
def plot_topology(linkslist, file):
    #plt.figure(figsize=(50, 50), dpi=300)
    G = nx.Graph()
    for e in linkslist:
        G.add_edge(e[0], e[1])
    pos = nx.layout.kamada_kawai_layout(G)

    #node_sizes = [3 + 10 * i for i in range(len(G))]
    node_size = 1
    M = G.number_of_edges()
    #edge_colors = range(2, M + 2)
    edge_colors = 2
    #edge_alphas = [(5 + i) / (M + 4) for i in range(M)]
    edge_alphas = 0.5

    #nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='blue')
    nodes = nx.draw_networkx_nodes(G, pos, node_size=0.1, node_color='blue')
    #edges = nx.draw_networkx_edges(G, pos, node_size=node_sizes, arrowstyle='->',
    #                               arrowsize=10, edge_color=edge_colors,
    #                               edge_cmap=plt.cm.Blues, width=2)
    edges = nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=1, width=0.05)
    # set alpha value for each edge
    #for i in range(M):
    #    edges[i].set_alpha(edge_alphas[i])

    #pc = mpl.collections.PatchCollection(edges, cmap=plt.cm.Blues)
    #pc.set_array(edge_colors)
    #pc = mpl.collections.PatchCollection(edges)
    #plt.colorbar(pc)
    plt.savefig(file, dpi=2000)


# dictionary with links as keys
# plots degree distribution graph
def test_degree_distribution(graph, file):
    g = nx.Graph(node_type=int)
    for e in graph:
        g.add_edge(e[0], e[1])

    #find giant component
    gcc = sorted(nx.connected_components(g), key=len, reverse=True)
    g0 = g.subgraph(gcc[0])

    degree_sequence = sorted((d for n, d in g.degree()), reverse=True)
    d_max = max(degree_sequence)

    degrees = np.arange(1, d_max)
    counter = []
    for i in degrees:
        counter.append(degree_sequence.count(i))
    counter_np = np.array(counter)


    cdf = counter_np.cumsum() / counter_np.sum()
    ccdf = 1 - cdf

    fig = plt.figure("Degree", figsize=(8, 8))
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12, 4))
    #ax1.plot(degrees, cdf, label='cdf')
    ax1.plot(degrees, ccdf, label='ccdf')
    ax1.legend()
    ax1.set_xscale("log")

    ax2.bar(degrees, cdf, label='cdf')
    #ax2.bar(degrees, ccdf, bottom=cdf, label='ccdf')
    ax2.margins(x=0.01)
    ax2.set_xticks(degrees)
    ax2.set_xticklabels([f'{y % 100:02d}' for y in degrees])
    ax2.set_xscale("log")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(file)
    plt.close()

#single event stats
def get_stats(graph, ns):
    stat = Stats()
    stat.nsample = ns

    g = nx.Graph(node_type=int)
    for e in graph:
        g.add_edge(e[0], e[1])

    #find giant component
    gcc = sorted(nx.connected_components(g), key=len, reverse=True)
    g0 = g.subgraph(gcc[0])

    #collecting node numbers
    stat.nodes_number = g.number_of_nodes()
    stat.size_of_giant_component = nx.number_of_nodes(g0)
    stat.disjoint_components = nx.number_connected_components(g)

    #sampling nodes for aspl approx.
    sampled_src = random.sample(g0.nodes, int(ns))
    sampled_dest = random.sample(g0.nodes, int(ns))

    count = 0
    sum = 0
    for s in sampled_src:
        for d in sampled_dest:
            if s != d:
                dist = nx.shortest_path_length(g0, s, d)
                count += 1
                sum += dist
    avg = sum/count
    stat.aspl = avg
    return stat

#plots variation of values, requires multiple events and list of stats
def plot_stat_variation(statList, filename):

    x = np.array(range(0, len(statList)))
    y_aspl = []
    y_sogc = []
    y_discomp = []
    y_int_damage = []
    y_pop_damage = []
    for i in statList:
        y_aspl.append(i.aspl)
        y_sogc.append(i.size_of_giant_component)
        y_discomp.append(i.disjoint_components)
        y_int_damage.append(i.internet_damage)
        y_pop_damage.append(i.user_damage)

    #aspl variation plot

    y = np.array(y_aspl)
    plt.plot(x, y)
    plt.savefig("aspl_" + str(filename))
    plt.close()

    #size of giant component variation plot

    y = np.array(y_sogc)
    plt.plot(x, y)
    plt.savefig("giant_component_" + str(filename))
    plt.close()

    #disjoint components variation

    y = np.array(y_discomp)
    plt.plot(x, y)
    plt.savefig("disjoin_components_" + str(filename))
    plt.close()

    #total internet damage progression
    y = np.array(y_int_damage)
    plt.plot(x, y)
    plt.savefig("damage_internet_" + str(filename))
    plt.close()

    #total population service lost
    y = np.array(y_pop_damage)
    plt.plot(x, y)
    plt.savefig("damage_population_" + str(filename))
    plt.close()
