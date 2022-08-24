import sys
from clingo.application import Application, clingo_main
from clingo.ast import ProgramBuilder, parse_files, Transformer, Variable, Rule, Position, Location
from clingo.control import Control
from clingo import ast
import re

class RuleChanger(Transformer):
    def __init__(self, ctl):
        self.counter = 0
        self.ctl = ctl
        self.rules = []

    def visit_Rule(self, node):
        pos = Position('<string>', 1, 1)
        loc = Location(pos, pos)
        fun = ast.Function(loc, '_r{}'.format(self.counter), [], False)
        atm = ast.SymbolicAtom(fun)
        lit = ast.Literal(loc, ast.Sign.NoSign, atm)

        self.rules.append(node)

        with ProgramBuilder(self.ctl) as bld:
            bld.add(ast.Rule(loc, node.head, [lit]))

        self.counter += 1
        return node.update(head=lit)


class CoverageCheck():
    def __init__(self, program, verbose=True):
        self.inputAtoms = set()
        self.posCov = set()
        self.negCov = set()
        self.numRules = 0
        self.program = program
        self.rules = []
        self.verbose = verbose
    
    def on_model(self, model):
        pos = []
        neg = []
        for match in re.finditer("_r[0-9]*", str(model)):
            pos.append(str(model)[match.start():match.end()])
        for i in range(self.numRules):
            if "_r"+str(i) not in pos:
                neg.append("_r"+str(i))
        self.posCov.update(pos)
        self.negCov.update(neg)

    def check_coverage(self, testcases):
        for file in testcases:
            ctl = Control(["0"], message_limit=0)
            transformer = RuleChanger(ctl)

            with ProgramBuilder(ctl) as builder:
                parse_files([self.program], lambda stm: builder.add(transformer(stm)))
                self.numRules = transformer.counter
                parse_files([file], builder.add)
            ctl.ground([("base", [])])
            ctl.solve(on_model=self.on_model)

        # print(self.posCov)
        # print(self.negCov)
        positive = (len(self.posCov)*100) / self.numRules
        negative = (len(self.negCov)*100) / self.numRules
        print(f"Positive rule coverage: {positive}% ({len(self.posCov)} out of {self.numRules} rules)")
        print(f"Negative rule coverage: {negative}% ({len(self.negCov)} out of {self.numRules} rules)")

        for rule in transformer.rules:
            self.rules.append(rule)

        if self.verbose and positive != 100.0:
            self.print_pos_coverage()
        if self.verbose and negative != 100.0:
            self.print_neg_coverage()

    def print_pos_coverage(self):
        cov = set([int(label[label.find("r")+1:]) for label in self.posCov])
        notcov = [idx for idx in range(self.numRules) if idx not in cov]

        print("\nRules that have not been positively covered:")
        for idx in notcov:
            print(str(self.rules[idx]) + " (line: {}, column: {})".format(self.rules[idx].location[0][1], self.rules[idx].location[0][2]))

    def print_neg_coverage(self):
        cov = set([int(label[label.find("r")+1:]) for label in self.negCov])
        notcov = [idx for idx in range(self.numRules) if idx not in cov]

        print("\nRules that have not been negatively covered:")
        for idx in notcov:
            print(str(self.rules[idx]) + " (line: {}, column: {})".format(self.rules[idx].location[0][1], self.rules[idx].location[0][2]))



def main():
    testcases = sys.argv[2:]
    program = sys.argv[1]

    check = CoverageCheck(program)
    check.check_coverage(testcases)


if __name__ == "__main__":
    main()