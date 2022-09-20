from clingo.ast import Transformer, Position, Location, ASTType, ProgramBuilder
from clingo import ast
from collections import defaultdict

class RuleTagger(Transformer):
    def __init__(self, ctl):
        self.counter = 0
        self.ctl = ctl
        self.rules = []
        self.heads = dict()

    def visit_Rule(self, node):
        pos = Position('<string>', 1, 1)
        loc = Location(pos, pos)
        fun = ast.Function(loc, '_r{}'.format(self.counter), [], False)
        atm = ast.SymbolicAtom(fun)
        lit = ast.Literal(loc, ast.Sign.NoSign, atm)

        self.rules.append(node)

        if str(node.head) != "#false":
            if node.head.ast_type == ASTType.Aggregate or node.head.ast_type == ASTType.Disjunction:
                for elem in node.head.elements:
                    if elem.literal not in self.heads.keys():
                        self.heads[elem.literal] = [[],[]]
                    self.heads[elem.literal][0].append(fun.name)
                    self.heads[elem.literal][1].append(elem.literal.location)
            elif node.head.ast_type == ASTType.Literal:
                if node.head not in self.heads.keys():
                    self.heads[node.head] = [[],[]]
                self.heads[node.head][0].append(fun.name)
                self.heads[node.head][1].append(node.head.location)

            # print(self.heads)

            with ProgramBuilder(self.ctl) as bld:
                bld.add(ast.Rule(loc, lit, node.body))

            self.counter += 1
            return node
        else:
            self.counter += 1
            return node.update(head=lit)