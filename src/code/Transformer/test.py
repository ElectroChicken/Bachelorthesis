from yaml import parse
import sys
from clingo import Control, ast
from clingo.ast import Location, ProgramBuilder, Position, parse_string, parse_files, Transformer

ctl = Control()

class Observer:
    def rule(self, choice, head, body):
        #rules.append([choice, head, body])
        print("rule:", choice, head, body)

    def external(self, atom, value):
        print("added external:", atom, value)

class RuleChanger(Transformer):
    counter = 0
    def visit_Rule(self, node):
        pos = Position('<string>', 1, 1)
        loc = Location(pos, pos)
        fun = ast.Function(loc, '_r{}'.format(self.counter), [], False)
        atm = ast.SymbolicAtom(fun)
        lit = ast.Literal(loc, ast.Sign.NoSign, atm)

        with ProgramBuilder(ctl) as bld:
            bld.add(ast.Rule(loc, node.head, [lit]))

        self.counter += 1
        return node.update(head=lit)

trans = RuleChanger()
#parse_string("p :- q. q :- s. s.", lambda stm: print(str(trans(stm))))

# ctl.register_observer(Observer())
ctl.configuration.solve.models = 0
with ProgramBuilder(ctl) as builder:
    # parse_string("d :- a, not b. e :- b. f :- a, c. d :- a.", lambda stm: builder.add(trans(stm)))
    # parse_string("a.", builder.add)
    parse_files([sys.argv[1]], lambda stm: builder.add(trans(stm)))
    parse_files([sys.argv[2]], builder.add)
ctl.ground([("base",[])])
print(ctl.solve(on_model=print))