from itertools import combinations
from clingo.ast import ASTType
import networkx as nx
from itertools import chain
    
def build_dependency_graph(rules):
    G = nx.DiGraph()
    for rule in rules:
        if str(rule.head) != "#false":
            if rule.body:
                for atom in rule.body:
                    if atom.sign == 0:
                        if rule.head.ast_type == ASTType.Aggregate:
                            for elem in rule.head.elements:
                                G.add_edge(atom, elem.literal)
                        elif rule.head.ast_type == ASTType.Literal:
                            G.add_edge(atom, rule.head)
    
    return G


def find_sccs(graph):
    # return sorted(nx.strongly_connected_components(graph))
    return [x for x in nx.strongly_connected_components(graph) if len(x)>1]


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