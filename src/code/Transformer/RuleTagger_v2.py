from clingo.ast import Transformer, Position, Location, ASTType, ProgramBuilder
from clingo import ast
from collections import defaultdict

class RuleTagger(Transformer):
    def __init__(self, ctl):
        self.counter = 0
        self.ctl = ctl
        self.rules = []
        self.heads = defaultdict(list)

    def visit_Rule(self, node):
        pos = Position('<string>', 1, 1)
        loc = Location(pos, pos)
        fun = ast.Function(loc, '_r{}'.format(self.counter), [], False)
        atm = ast.SymbolicAtom(fun)
        lit = ast.Literal(loc, ast.Sign.NoSign, atm)

        self.rules.append(node)

        if str(node.head) != "#false":
            if node.head.ast_type == ASTType.Aggregate:
                for elem in node.head.elements:
                    self.heads[elem.literal].append(fun.name)
            elif node.head.ast_type == ASTType.Literal:
                self.heads[node.head].append(fun.name)
            # print(self.heads)

            with ProgramBuilder(self.ctl) as bld:
                bld.add(ast.Rule(loc, lit, node.body))

            self.counter += 1
            return node
        else:
            self.counter += 1
            return node.update(head=lit)