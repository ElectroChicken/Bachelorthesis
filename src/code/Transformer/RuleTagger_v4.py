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
                    key = (elem.literal.atom.symbol.name, len(elem.literal.atom.symbol.arguments))
                    if key not in self.heads.keys():
                        self.heads[key] = [[],[]]
                    self.heads[key][0].append(fun.name)
                    self.heads[key][1].append(elem.literal.location)
            elif node.head.ast_type == ASTType.Literal:
                key = (node.head.atom.symbol.name, len(node.head.atom.symbol.arguments))
                if key not in self.heads.keys():
                    self.heads[key] = [[],[]]
                self.heads[key][0].append(fun.name)
                self.heads[key][1].append(node.head.location)

            # print(self.heads)

            with ProgramBuilder(self.ctl) as bld:
                bld.add(ast.Rule(loc, lit, node.body))

            self.counter += 1
            return node
        else:
            self.counter += 1
            return node.update(head=lit)