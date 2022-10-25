from itertools import combinations, chain
from clingo.ast import ASTType
import networkx as nx
import matplotlib.pyplot as plt
    
def build_dependency_graph(rules, heads):
    G = nx.DiGraph()
    G.add_nodes_from(heads)
    for rule in rules:
        if str(rule.head) != "#false":
            if rule.body:
                for atom in rule.body:
                    # print(atom.ast_type)
                    if atom.ast_type == ASTType.ConditionalLiteral:
                        pass        # !!!! TODO
                    else:
                        # add body atoms as nodes even if they are not connected?
                        if atom.sign == 0:
                            if rule.head.ast_type == ASTType.Aggregate or rule.head.ast_type == ASTType.Disjunction:
                                for elem in rule.head.elements:
                                    G.add_edge((atom.atom.symbol.name, len(atom.atom.symbol.arguments)), (elem.literal.atom.symbol.name, len(elem.literal.atom.symbol.arguments)))
                            elif rule.head.ast_type == ASTType.Literal:
                                G.add_edge((atom.atom.symbol.name, len(atom.atom.symbol.arguments)), (rule.head.atom.symbol.name, len(rule.head.atom.symbol.arguments)))

    # nx.draw(G, with_labels=True)
    # plt.show()
    return G


def find_sccs(graph):
    return sorted(nx.strongly_connected_components(graph))
    # return [x for x in nx.strongly_connected_components(graph) if len(x)>1]


def find_loops(graph, sccs):
    loops = set()
    for scc in sccs:
        for subset in powerset(scc):
            if nx.is_strongly_connected(graph.subgraph(subset)):
                loops.add(subset)

    return loops


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s,r) for r in range(2,len(s)+1))