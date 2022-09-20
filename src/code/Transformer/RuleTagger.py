from clingo.ast import Transformer, Position, Location, ASTType, ProgramBuilder
from clingo import ast

class RuleTagger(Transformer):
    def __init__(self, ctl):
        self.counter = 0
        self.ctl = ctl
        self.rules = []
        self.heads = set()

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
                    self.heads.add(elem.literal)
            elif node.head.ast_type == ASTType.Literal:
                self.heads.add(node.head)
            # print(self.heads)

            with ProgramBuilder(self.ctl) as bld:
                bld.add(ast.Rule(loc, lit, node.body))

            self.counter += 1
            return node
        else:
            self.counter += 1
            return node.update(head=lit)