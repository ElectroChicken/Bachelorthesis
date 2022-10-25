from clingo.ast import Transformer, Position, Location, ASTType, ProgramBuilder
from clingo import ast
from collections import defaultdict

class RuleTagger(Transformer):
    def __init__(self, ctl):
        self.counter = 0
        self.ctl = ctl
        self.rules = []
        self.heads = dict()
        self.ndef = 0

    def visit_Rule(self, node):
        pos = Position('<string>', 1, 1)
        loc = Location(pos, pos)
        fun = ast.Function(loc, '_r{}'.format(self.counter), [], False)
        atm = ast.SymbolicAtom(fun)
        lit = ast.Literal(loc, ast.Sign.NoSign, atm)

        self.rules.append(node)

        if str(node.head) != "#false":
            with ProgramBuilder(self.ctl) as bld:
                if node.head.ast_type == ASTType.Aggregate or node.head.ast_type == ASTType.Disjunction:
                    for elem in node.head.elements:
                        key = (elem.literal.atom.symbol.name, len(elem.literal.atom.symbol.arguments))
                        if key not in self.heads.keys():
                            self.heads[key] = [[self.ndef],[elem.literal.location]]
                            id = self.ndef
                            self.ndef += 1
                        else:
                            self.heads[key][1].append(elem.literal.location)
                            id = self.heads[key][0][0]
                        fun2 = ast.Function(loc, '_d{}'.format(id), [], False)
                        atm2 = ast.SymbolicAtom(fun2)
                        lit2 = ast.Literal(loc, ast.Sign.NoSign, atm2)
                        bld.add(ast.Rule(loc, lit2, [lit]))
                elif node.head.ast_type == ASTType.Literal:
                    key = (node.head.atom.symbol.name, len(node.head.atom.symbol.arguments))
                    if key not in self.heads.keys():
                        self.heads[key] = [[self.ndef],[node.head.location]]
                        id = self.ndef
                        self.ndef += 1
                    else:
                        self.heads[key][1].append(node.head.location)
                        id = self.heads[key][0][0]
                    fun2 = ast.Function(loc, '_d{}'.format(id), [], False)
                    atm2 = ast.SymbolicAtom(fun2)
                    lit2 = ast.Literal(loc, ast.Sign.NoSign, atm2)
                    bld.add(ast.Rule(loc, lit2, [lit]))
                # print(self.heads)
                bld.add(ast.Rule(loc, lit, node.body))

            self.counter += 1
            return node
        else:
            self.counter += 1
            return node.update(head=lit)