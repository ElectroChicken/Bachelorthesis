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
                for atm in rule.body:
                    if atm.ast_type == ASTType.Literal:
                        if atm.atom.ast_type == ASTType.SymbolicAtom:
                            if atm.sign == 0:
                                if atm.atom.symbol.ast_type == ASTType.Pool:
                                    keyB = (atm.atom.symbol.arguments[0].name, len(atm.atom.symbol.arguments[0].arguments))
                                else:
                                    keyB = (atm.atom.symbol.name, len(atm.atom.symbol.arguments))
                                G.add_edges_from(edges_from(keyB, rule))
                        elif atm.atom.ast_type == ASTType.Aggregate:
                            for elem in atm.atom.elements:
                                if elem.literal.atom.ast_type == ASTType.SymbolicAtom:
                                    if elem.literal.sign == 0:
                                        if elem.literal.atom.symbol.ast_type == ASTType.Pool:
                                            keyB = (elem.literal.atom.symbol.arguments[0].name, len(elem.literal.atom.symbol.arguments[0].arguments))
                                        else:
                                            keyB = (elem.literal.atom.symbol.name, len(elem.literal.atom.symbol.arguments))
                                        G.add_edges_from(edges_from(keyB, rule))
                                for lit in elem.condition:
                                    pass # ??? is this relevent for the dependency graph?
                        elif atm.atom.ast_type == ASTType.BodyAggregate:
                            pass # ???
                    elif atm.ast_type == ASTType.ConditionalLiteral:
                        if atm.literal.atom.ast_type == ASTType.SymbolicAtom:
                            if atm.literal.sign == 0:
                                if atm.literal.atom.symbol.ast_type == ASTType.Pool:
                                    keyB = (atm.literal.atom.symbol.arguments[0].name, len(atm.literal.atom.symbol.arguments[0].arguments))
                                else:
                                    keyB = (atm.literal.atom.symbol.name, len(atm.literal.atom.symbol.arguments))
                                G.add_edges_from(edges_from(keyB, rule))
                        for lit in atm.condition:
                            pass # ???
    # nx.draw(G, with_labels=True)
    # plt.show()
    return G

def edges_from(keyB, rule):
    edges = []
    if rule.head.ast_type == ASTType.Literal:
        if rule.head.atom.ast_type == ASTType.SymbolicAtom:
            if rule.head.sign == 0:
                if rule.head.atom.symbol.ast_type == ASTType.Pool:
                    keyH = (rule.head.atom.symbol.arguments[0].name, len(rule.head.atom.symbol.arguments[0].arguments))
                else:
                    keyH = (rule.head.atom.symbol.name, len(rule.head.atom.symbol.arguments))
                edges.append((keyB, keyH))
    elif rule.head.ast_type == ASTType.Aggregate or rule.head.ast_type == ASTType.Disjunction:
        for elem in rule.head.elements:
            if elem.literal.atom.ast_type == ASTType.SymbolicAtom:
                if elem.literal.sign == 0:
                    if elem.literal.atom.symbol.ast_type == ASTType.Pool:
                        keyH = (elem.literal.atom.symbol.arguments[0].name, len(elem.literal.atom.symbol.arguments[0].arguments))
                    else:
                        keyH = (elem.literal.atom.symbol.name, len(elem.literal.atom.symbol.arguments))
                    edges.append((keyB, keyH))
    elif rule.head.ast_type == ASTType.HeadAggregate:
        for elem in rule.head.elements:
            if elem.condition.literal.atom.ast_type == ASTType.SymbolicAtom:
                if elem.condition.literal.sign == 0:
                    if elem.condition.literal.atom.symbol.ast_type == ASTType.Pool:
                        keyH = (elem.condition.literal.atom.symbol.arguments[0].name, len(elem.condition.literal.atom.symbol.arguments[0].arguments))
                    else:
                        keyH = (elem.condition.literal.atom.symbol.name, len(elem.condition.literal.atom.symbol.arguments))
                    edges.append((keyB, keyH))
    return edges


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