from clingo.ast import ProgramBuilder, parse_files
from clingo.control import Control
from collections import defaultdict
from RuleTagger import RuleTagger
from dependencygraph_tools import build_dependency_graph, find_sccs, find_loops

class CoverageCheck():
    def __init__(self):
        self.posRCov = set()
        self.negRCov = set()
        self.posDCov = set()
        self.negDCov = set()
        self.numRules = 0
        self.rules = []
        self.heads = []
    
    def on_model(self, model):
        self.atoms = [atm for atm in model.symbols(atoms=True)]

    def check_model(self):
        # for rule coverage
        posR = []
        negR = []
        # for definition coverage
        posD = []
        negD = []
        atoms = []
        
        for atm in self.atoms:
            if atm.name.startswith("_"):
                posR.append(atm.name)
            else:
                atoms.append(atm.name)
        for i in range(self.numRules):
            if "_r"+str(i) not in posR:
                negR.append("_r"+str(i))

        for atm in self.heads:
            if str(atm) in atoms:
                posD.append(str(atm))
            else:
                negD.append(str(atm))

        self.posRCov.update(posR)
        self.negRCov.update(negR)
        self.posDCov.update(posD)
        self.negDCov.update(negD)

    def check_coverage(self, program, testcases, verbose=True):
        self.program = program
        self.verbose = verbose
        for file in testcases:
            ctl = Control(["0"], message_limit=0)
            transformer = RuleTagger(ctl)

            with ProgramBuilder(ctl) as builder:
                parse_files([self.program], lambda stm: builder.add(transformer(stm)))
                self.numRules = transformer.counter
                self.heads = transformer.heads
                parse_files([file], builder.add)
            
            if self.numRules == 0:
                self.numRules = transformer.counter
            if not self.heads:
                self.heads = transformer.heads
            if not self.rules:
                self.rules = transformer.rules

            ctl.ground([("base", [])])
            ctl.configuration.solve.enum_mode = "cautious"
            ctl.solve(on_model=self.on_model)
            self.check_model()

            ctl.configuration.solve.enum_mode = "brave"
            ctl.solve(on_model=self.on_model)
            self.check_model()

        positiveR = (len(self.posRCov)*100) / self.numRules
        negativeR = (len(self.negRCov)*100) / self.numRules
        print(f"Positive rule coverage: {positiveR}% ({len(self.posRCov)} out of {self.numRules} rules)")
        print(f"Negative rule coverage: {negativeR}% ({len(self.negRCov)} out of {self.numRules} rules)")

        positiveD = (len(self.posDCov)*100) / len(self.heads)
        negativeD = (len(self.negDCov)*100) / len(self.heads)
        print(f"\nPositive definition coverage: {positiveD}% ({len(self.posDCov)} out of {len(self.heads)} atoms)")
        print(f"Negative definition coverage: {negativeD}% ({len(self.negDCov)} out of {len(self.heads)} atoms)")

        graph = build_dependency_graph(self.rules)
        sccs = find_sccs(graph)
        loops = find_loops(graph, sccs)
        print(sccs)
        print(loops)
        print(self.posRCov)

        # self.verbose=False
        if self.verbose and positiveR != 100.0:
            self.print_pos_Rcoverage()
        if self.verbose and negativeR != 100.0:
            self.print_neg_Rcoverage()
        if self.verbose and positiveD != 100.0:
            self.print_pos_Dcoverage()
        if self.verbose and negativeD != 100.0:
            self.print_neg_Dcoverage()

    def print_pos_Rcoverage(self):
        cov = set([int(label[2:]) for label in self.posRCov])
        notcov = [idx for idx in range(self.numRules) if idx not in cov]

        print("\nRules that have not been positively rule-covered:")
        for idx in notcov:
            print(str(self.rules[idx]) + "\nline: {}, column: {}".format(self.rules[idx].location[0][1], self.rules[idx].location[0][2]))

    def print_neg_Rcoverage(self):
        cov = set([int(label[2:]) for label in self.negRCov])
        notcov = [idx for idx in range(self.numRules) if idx not in cov]

        print("\nRules that have not been negatively rule-covered:")
        for idx in notcov:
            print(str(self.rules[idx]) + "\nline: {}, column: {}".format(self.rules[idx].location[0][1], self.rules[idx].location[0][2]))

    def print_pos_Dcoverage(self):
        locations = defaultdict(list)
        for head in self.heads:
            if str(head) not in self.posDCov:
                locations[str(head)].append(head.location)

        print("\nAtoms that have not been positively definition-covered:")
        for atm, locs in locations.items():
            print(atm)
            for loc in locs:
                print("line: {}, column: {}".format(loc.begin[1], loc.begin[2]))

    def print_neg_Dcoverage(self):
        locations = defaultdict(list)
        for head in self.heads:
            if str(head) not in self.negDCov:
                locations[str(head)].append(head.location)

        print("\nAtoms that have not been negatively definition-covered:")
        for atm, locs in locations.items():
            print(atm)
            for loc in locs:
                print("line: {}, column: {}".format(loc.begin[1], loc.begin[2]))
