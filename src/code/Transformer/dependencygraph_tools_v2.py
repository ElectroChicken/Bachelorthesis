import networkx as nx
from clingo.ast import ASTType
from itertools import combinations, chain

import matplotlib.pyplot as plt
    
def build_dependency_graph(rules, atoms):
    G = nx.DiGraph()
    G.add_nodes_from(atoms)
    for rule in rules:
        if str(rule.head) != "#false":
            if rule.body:
                for atm in rule.body:
                    if atm.ast_type == ASTType.Literal:
                        if atm.atom.ast_type == ASTType.SymbolicAtom:
                            if atm.sign == 0:
                                if atm.atom.symbol.ast_type == ASTType.Pool:
                                    keyB = (atm.atom.symbol.arguments[0].name, len(atm.atom.symbol.arguments[0].arguments))
                                elif atm.atom.symbol.ast_type == ASTType.Function:
                                    keyB = (atm.atom.symbol.name, len(atm.atom.symbol.arguments))
                                G.add_edges_from(edges_to(keyB, rule))
                        elif atm.atom.ast_type == ASTType.Aggregate:
                            for elem in atm.atom.elements:
                                if elem.literal.atom.ast_type == ASTType.SymbolicAtom:
                                    if elem.literal.sign == 0:
                                        if elem.literal.atom.symbol.ast_type == ASTType.Pool:
                                            keyB = (elem.literal.atom.symbol.arguments[0].name, len(elem.literal.atom.symbol.arguments[0].arguments))
                                        elif elem.literal.atom.symbol.ast_type == ASTType.Function:
                                            keyB = (elem.literal.atom.symbol.name, len(elem.literal.atom.symbol.arguments))
                                        G.add_edges_from(edges_to(keyB, rule))
                        elif atm.atom.ast_type == ASTType.BodyAggregate:
                            for elem in atm.atom.elements:
                                for cond in elem.condition:
                                    if cond.ast_type == ASTType.Literal:
                                        if cond.atom.ast_type == ASTType.SymbolicAtom:
                                            if cond.sign == 0:
                                                if cond.atom.symbol.ast_type == ASTType.Pool:
                                                    keyB = (cond.atom.symbol.arguments[0].name, len(cond.atom.symbol.arguments[0].arguments))
                                                elif cond.atom.symbol.ast_type == ASTType.Function:
                                                    keyB = (cond.atom.symbol.name, len(cond.atom.symbol.arguments))
                                                G.add_edges_from(edges_to(keyB, rule))
                    elif atm.ast_type == ASTType.ConditionalLiteral:
                        if atm.literal.atom.ast_type == ASTType.SymbolicAtom:
                            if atm.literal.sign == 0:
                                if atm.literal.atom.symbol.ast_type == ASTType.Pool:
                                    keyB = (atm.literal.atom.symbol.arguments[0].name, len(atm.literal.atom.symbol.arguments[0].arguments))
                                elif atm.literal.atom.symbol.ast_type == ASTType.Function:
                                    keyB = (atm.literal.atom.symbol.name, len(atm.literal.atom.symbol.arguments))
                                G.add_edges_from(edges_to(keyB, rule))
    # nx.draw(G, with_labels=True)
    # plt.show()
    return G

def edges_to(keyB, rule):
    edges = []
    if rule.head.ast_type == ASTType.Literal:
        if rule.head.atom.ast_type == ASTType.SymbolicAtom:
            if rule.head.sign == 0:
                if rule.head.atom.symbol.ast_type == ASTType.Pool:
                    keyH = (rule.head.atom.symbol.arguments[0].name, len(rule.head.atom.symbol.arguments[0].arguments))
                elif rule.head.atom.symbol.ast_type == ASTType.Function:
                    keyH = (rule.head.atom.symbol.name, len(rule.head.atom.symbol.arguments))
                edges.append((keyH, keyB))
    elif rule.head.ast_type == ASTType.Aggregate or rule.head.ast_type == ASTType.Disjunction:
        for elem in rule.head.elements:
            if elem.literal.atom.ast_type == ASTType.SymbolicAtom:
                if elem.literal.sign == 0:
                    if elem.literal.atom.symbol.ast_type == ASTType.Pool:
                        keyH = (elem.literal.atom.symbol.arguments[0].name, len(elem.literal.atom.symbol.arguments[0].arguments))
                    elif elem.literal.atom.symbol.ast_type == ASTType.Function:
                        keyH = (elem.literal.atom.symbol.name, len(elem.literal.atom.symbol.arguments))
                    edges.append((keyH, keyB))
    elif rule.head.ast_type == ASTType.HeadAggregate:
        for elem in rule.head.elements:
            if elem.condition.literal.atom.ast_type == ASTType.SymbolicAtom:
                if elem.condition.literal.sign == 0:
                    if elem.condition.literal.atom.symbol.ast_type == ASTType.Pool:
                        keyH = (elem.condition.literal.atom.symbol.arguments[0].name, len(elem.condition.literal.atom.symbol.arguments[0].arguments))
                    elif elem.condition.literal.atom.symbol.ast_type == ASTType.Function:
                        keyH = (elem.condition.literal.atom.symbol.name, len(elem.condition.literal.atom.symbol.arguments))
                    edges.append((keyH, keyB))
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
    return chain.from_iterable(combinations(s,r) for r in range(1,len(s)+1))