from distutils.command import build
from clingo.ast import ProgramBuilder, parse_files
from clingo.control import Control
from collections import defaultdict
import networkx as nx
# from RuleTagger_v2 import RuleTagger
from RuleTagger_v3 import RuleTagger
from dependencygraph_tools import build_dependency_graph, find_sccs, find_loops

class CoverageCheck():
    def __init__(self):
        self.posRCov = set()
        self.negRCov = set()
        self.posDCov = set()
        self.negDCov = set()
        self.posLCov = set()
        self.negLCov = set()
        self.posCCov = set()
        self.negCCov = set()        
        self.numRules = 0
        self.rules = []
        self.heads = defaultdict(list)
        self.loops = set()
        self.sccs = []
        self.graph = nx.DiGraph()
    
    def on_model_loop(self, model):
        self.atoms = set([atm.name for atm in model.symbols(atoms=True) if atm.name.startswith("_")])
        print(model)

        self.check_loop()

        self.check_rule_positive()
        self.check_rule_negative()
        self.check_definition()

    def on_model_scc(self, model):
        self.atoms = set([atm.name for atm in model.symbols(atoms=True) if atm.name.startswith("_")])
        print(model)

        self.check_component()

        self.check_rule_positive()
        self.check_rule_negative()
        self.check_definition()

    def on_model(self, model):
        self.atoms = set([atm.name for atm in model.symbols(atoms=True) if atm.name.startswith("_")])
        print(model)

    def check_rule_positive(self):
        self.posRCov.update(self.atoms)

    def check_rule_negative(self):
        for i in range(self.numRules):
            if "_r"+str(i) not in self.atoms:
                self.negRCov.add("_r"+str(i))

    def check_definition(self):
        for atm, body in self.heads.items():
            if self.atoms.intersection(body[0]):
                self.posDCov.add(atm)
            else:
                self.negDCov.add(atm)

    def check_definition_positive(self):
        for atm, body in self.heads.items():
            if self.atoms.intersection(body[0]):
                self.posDCov.add(atm)

    def check_definition_negative(self):
        for atm, body in self.heads.items():
            if not self.atoms.intersection(body[0]):
                self.negDCov.add(atm)                

    def check_component(self):
        for scc in self.sccs:
            if all(self.atoms.intersection(self.heads[atm][0]) for atm in scc):
                self.posCCov.add(tuple(scc))
            elif all(not self.atoms.intersection(self.heads[atm][0]) for atm in scc):
                self.negCCov.add(tuple(scc))

    def check_loop(self):
        for loop in self.loops:
            covered = True
            for atm in loop:
                if not self.atoms.intersection(self.heads[atm][0]):
                    covered = False
                    break
            if covered:
                self.posLCov.add(loop)
            else:
                self.negLCov.add(loop)

    def check_positive(self):
        self.posRCov.update(self.atoms)

        for atm, body in self.heads.items():
            if self.atoms.intersection(body[0]):
                self.posDCov.add(atm)

    def check_negative(self):
        for i in range(self.numRules):
            if "_r"+str(i) not in self.atoms:
                self.negRCov.add("_r"+str(i))

        for atm, body in self.heads.items():
            if not self.atoms.intersection(body[0]):
                self.negDCov.add(atm)

    def check_coverage(self, program, testcases, verbose=True, loop="loop"):
        for file in testcases:
            ctl = Control(["0"], message_limit=0)
            transformer = RuleTagger(ctl)
            with ProgramBuilder(ctl) as builder:
                parse_files([program], lambda stm: builder.add(transformer(stm)))
                parse_files([file], builder.add)

            if self.numRules == 0:
                self.numRules = transformer.counter
            if not self.heads:
                self.heads = transformer.heads
            if not self.rules:
                self.rules = transformer.rules

            ctl.ground([("base", [])])

            loop="loop"
            if loop == "loop":
                if not self.graph:
                    self.graph = build_dependency_graph(self.rules)
                if not self.sccs:
                    self.sccs = find_sccs(self.graph)
                if not self.loops:
                    self.loops = find_loops(self.graph, self.sccs)
                res = ctl.solve(on_model=self.on_model_loop)
                if not res.satisfiable:
                    print("Please enter a correct Testcase (solve call unsatisfiable)")
                    return 0
            elif loop == "scc":
                if not self.graph:
                    self.graph = build_dependency_graph(self.rules)
                if not self.sccs:
                    self.sccs = find_sccs(self.graph)
                res = ctl.solve(on_model=self.on_model_scc)
                if not res.satisfiable:
                    print("Please enter a correct Testcase (solve call unsatisfiable)")
                    return 0
            else:
                ctl.configuration.solve.enum_mode = "cautious"
                res = ctl.solve(on_model=self.on_model)
                if res.satisfiable:
                    self.check_rule_negative()
                    self.check_definition_negative()
                    ctl.configuration.solve.enum_mode = "brave"
                    ctl.solve(on_model=self.on_model)
                    self.check_rule_positive()
                    self.check_definition_positive()
                else:
                    print("Please enter a correct Testcase (solve call unsatisfiable)")
                    return 0

        positiveR = (len(self.posRCov)*100) / self.numRules
        negativeR = (len(self.negRCov)*100) / self.numRules
        print(f"Positive rule coverage: {positiveR}% ({len(self.posRCov)} out of {self.numRules} rules)")
        print(f"Negative rule coverage: {negativeR}% ({len(self.negRCov)} out of {self.numRules} rules)")
        if verbose and positiveR != 100.0:
            self.print_pos_Rcoverage()
        if verbose and negativeR != 100.0:
            self.print_neg_Rcoverage()

        positiveD = (len(self.posDCov)*100) / len(self.heads)
        negativeD = (len(self.negDCov)*100) / len(self.heads)
        print(f"\nPositive definition coverage: {positiveD}% ({len(self.posDCov)} out of {len(self.heads)} atoms)")
        print(f"Negative definition coverage: {negativeD}% ({len(self.negDCov)} out of {len(self.heads)} atoms)")
        if verbose and positiveD != 100.0:
            self.print_pos_Dcoverage()
        if verbose and negativeD != 100.0:
            self.print_neg_Dcoverage()

        if loop == "loop":
            positiveL = ((len(self.posLCov) + len(self.posDCov)) * 100) / (len(self.heads) + len(self.loops))
            negativeL = ((len(self.negLCov) + len(self.negDCov)) * 100) / (len(self.heads) + len(self.loops))
            print(f"\nPositive loop coverage: {positiveL}% ({len(self.posLCov) + len(self.posDCov)} out of {len(self.heads) + len(self.loops)} loops)")
            print(f"Negative loop coverage: {negativeL}% ({len(self.negLCov) + len(self.negDCov)} out of {len(self.heads) + len(self.loops)} loops)")
            if verbose and positiveL != 100.0:
                self.print_pos_Lcoverage()
            if verbose and negativeL != 100.0:
                self.print_neg_Lcoverage()
        
        elif loop == "scc":
            if len([scc for scc in self.sccs if len(scc) > 1]):
                positiveC = (len(self.posCCov) * 100) / (len([scc for scc in self.sccs if len(scc) > 1]))
                negativeC = (len(self.negCCov) * 100) / (len([scc for scc in self.sccs if len(scc) > 1]))
                print(f"\nPositive component coverage: {positiveC}% ({len(self.posCCov)} out of {len([scc for scc in self.sccs if len(scc) > 1])} components)")
                print(f"Negative component coverage: {negativeC}% ({len(self.negCCov)} out of {len([scc for scc in self.sccs if len(scc) > 1])} components)")
                if verbose and positiveC != 100.0:
                    self.print_pos_Ccoverage()
                if verbose and negativeC != 100.0:
                    self.print_neg_Ccoverage()
            else:
                print("\nNo SCCs in the program!")

        # for loop in self.loops:
        #     print([atm.atom.symbol.name for atm in loop])
        # for scc in self.sccs:
        #     print([atm.atom.symbol.name for atm in scc])
        # print(self.posLCov)
        # print(self.negLCov)
        # print(self.posRCov)
        # print(self.posDCov)
        # print(self.negRCov)
        # print(self.negDCov)   
        print(self.heads) 
        # print(self.rules)    
           

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
            if head not in self.posDCov:
                locations[str(head)].append(self.heads[head][1])

        print("\nAtoms that have not been positively definition-covered:")
        for atm, locs in locations.items():
            print(atm)
            for loc in locs[0]:
                print("line: {}, column: {}".format(loc.begin[1], loc.begin[2]))

    def print_neg_Dcoverage(self):
        locations = defaultdict(list)
        for head in self.heads:
            if head not in self.negDCov:
                locations[str(head)].append(self.heads[head][1])

        print("\nAtoms that have not been negatively definition-covered:")
        for atm, locs in locations.items():
            print(atm)
            for loc in locs[0]:
                print("line: {}, column: {}".format(loc.begin[1], loc.begin[2]))

    def print_pos_Lcoverage(self):
        locations = defaultdict(list)
        for loop in self.loops:
            if loop not in self.posLCov:
                for atm in loop:
                    locations[loop].append(self.heads[atm][1])

        print("\nLoops that have not been positively loop-covered:")
        for loop, locs in locations.items():
            print([atm.atom.symbol.name for atm in loop])
            for i in range(len(loop)):
                print(loop[i].atom.symbol.name)
                for j in range(len(locs[i])):
                    print("line: {}, column: {}".format(locs[i][j].begin[1], locs[i][j].begin[2]))

    def print_neg_Lcoverage(self):
        locations = defaultdict(list)
        for loop in self.loops:
            if loop not in self.negLCov:
                for atm in loop:
                    locations[loop].append(self.heads[atm][1])

        print("\nLoops that have not been negatively loop-covered:")
        for loop, locs in locations.items():
            print([atm.atom.symbol.name for atm in loop])
            for i in range(len(loop)):
                print(loop[i].atom.symbol.name)
                for j in range(len(locs[i])):
                    print("line: {}, column: {}".format(locs[i][j].begin[1], locs[i][j].begin[2]))

    def print_pos_Ccoverage(self):
        locations = defaultdict(list)
        for scc in self.sccs:
            if scc not in self.posCCov:
                for atm in scc:
                    locations[tuple(scc)].append(self.heads[atm][1])

        print("\nComponents that have not been positively component-covered:")
        for scc, locs in locations.items():
            print([atm.atom.symbol.name for atm in scc])
            for i in range(len(scc)):
                print(scc[i].atom.symbol.name)
                for j in range(len(locs[i])):
                    print("line: {}, column: {}".format(locs[i][j].begin[1], locs[i][j].begin[2]))

    def print_neg_Ccoverage(self):
        locations = defaultdict(list)
        for scc in self.sccs:
            if scc not in self.negCCov:
                for atm in scc:
                    locations[tuple(scc)].append(self.heads[atm][1])

        print("\nComponents that have not been negatively component-covered:")
        for scc, locs in locations.items():
            print([atm.atom.symbol.name for atm in scc])
            for i in range(len(scc)):
                print(scc[i].atom.symbol.name)
                for j in range(len(locs[i])):
                    print("line: {}, column: {}".format(locs[i][j].begin[1], locs[i][j].begin[2]))