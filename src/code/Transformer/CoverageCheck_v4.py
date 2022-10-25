from distutils.command import build
from clingo.ast import ProgramBuilder, parse_files, ASTType
from clingo.control import Control
from clingo import ast
from collections import defaultdict
import networkx as nx
from RuleTagger_v5 import RuleTagger
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
        self.numDef = 0
        self.numTestcases = 0
        self.rules = []
        self.heads = dict()
        self.loops = set()
        self.sccs = []
        self.graph = nx.DiGraph()
    

    def on_model(self, model):
        self.atoms = set([atm.name for atm in model.symbols(atoms=True) if atm.name.startswith("_")])
        print(model)


    def add_loops(self, ctl):
        num_loops = 0
        with ProgramBuilder(ctl) as bld:
            for loop in self.loops:
                body = []
                pos = ast.Position('<string>', 1, 1)
                loc = ast.Location(pos, pos)
                fun = ast.Function(loc, '_l{}'.format(num_loops), [], False)
                atm = ast.SymbolicAtom(fun)
                head = ast.Literal(loc, ast.Sign.NoSign, atm)
                for lit in loop:
                    key = (lit.atom.symbol.name, len(lit.atom.symbol.arguments))
                    fun = ast.Function(loc, '_d{}'.format(self.heads[key][0][0]), [], False)
                    atm = ast.SymbolicAtom(fun)
                    lit = ast.Literal(loc, ast.Sign.NoSign, atm)
                    body.append(lit)
                bld.add(ast.Rule(loc, head, body))
                num_loops += 1
            
    def add_sccs(self, ctl):
        num_sccs = 0
        with ProgramBuilder(ctl) as bld:
            for scc in self.sccs:
                body = []
                pos = ast.Position('<string>', 1, 1)
                loc = ast.Location(pos, pos)
                fun = ast.Function(loc, '_s{}'.format(num_sccs), [], False)
                atm = ast.SymbolicAtom(fun)
                head = ast.Literal(loc, ast.Sign.NoSign, atm)
                for lit in scc:
                    key = (lit.atom.symbol.name, len(lit.atom.symbol.arguments))
                    fun = ast.Function(loc, '_d{}'.format(self.heads[key][0][0]), [], False)
                    atm = ast.SymbolicAtom(fun)
                    lit = ast.Literal(loc, ast.Sign.NoSign, atm)
                    body.append(lit)
                bld.add(ast.Rule(loc, head, body))
                # print(ast.Rule(loc, head, body))
                num_sccs += 1

    def add_input(self, node):
        if not node.ast_type == ASTType.Program:
            pos = ast.Position('<string>', 1, 1)
            loc = ast.Location(pos, pos)
            fun = ast.Function(loc, '_i{}'.format(self.numTestcases), [], False)
            atm = ast.SymbolicAtom(fun)
            body = ast.Literal(loc, ast.Sign.NoSign, atm)
            with ProgramBuilder(self.ctl) as bld:
                bld.add(ast.Rule(loc, node.head, [body]))

    def check_rule_positive(self):
        self.posRCov.update(set([label for label in self.atoms if label.startswith("_r")]))

    def check_rule_negative(self):
        for i in range(self.numRules):
            if "_r"+str(i) not in self.atoms:
                self.negRCov.add("_r"+str(i))

    def check_definition_positive(self):
        self.posDCov.update(set([label for label in self.atoms if label.startswith("_d")]))

    def check_definition_negative(self):
        for i in range(self.numDef):
            if "_d"+str(i) not in self.atoms:
                self.negDCov.add("_d"+str(i))

    def check_component_positive(self):
        self.posCCov.update(set([label for label in self.atoms if label.startswith("_s")]))

    def check_component_negative(self):
        for i in range(len(self.sccs)):
            if "_s"+str(i) not in self.atoms:
                self.negCCov.add("_s"+str(i))

    def check_loop_positive(self):
        self.posLCov.update(set([label for label in self.atoms if label.startswith("_l")]))

    def check_loop_negative(self):
        for i in range(len(self.loops)):
            if "_l"+str(i) not in self.atoms:
                self.negLCov.add("_l"+str(i))


    def check_coverage(self, program, testcases, verbose=True, loop="loop"):
        for file in testcases:
            self.ctl = Control(["0"], message_limit=0)
            transformer = RuleTagger(self.ctl)
            with ProgramBuilder(self.ctl) as builder:
                parse_files([program], lambda stm: builder.add(transformer(stm)))
                parse_files([file], builder.add)

            if self.numRules == 0:
                self.numRules = transformer.counter
            if self.numDef == 0:
                self.numDef = transformer.ndef
            if not self.heads:
                self.heads = transformer.heads
            if not self.rules:
                self.rules = transformer.rules
            


            loop="loop"
            if loop == "loop":
                if not self.graph:
                    self.graph = build_dependency_graph(self.rules)
                if not self.sccs:
                    self.sccs = find_sccs(self.graph)
                if not self.loops:
                    self.loops = find_loops(self.graph, self.sccs)
                self.add_loops(self.ctl)
                self.ctl.ground([("base", [])])
                self.ctl.configuration.solve.enum_mode = "cautious"
                res = self.ctl.solve(on_model=self.on_model)
                if res.satisfiable:
                    self.check_rule_negative()
                    self.check_definition_negative()
                    self.check_loop_negative()
                    self.ctl.configuration.solve.enum_mode = "brave"
                    self.ctl.solve(on_model=self.on_model)
                    self.check_rule_positive()
                    self.check_definition_positive()
                    self.check_loop_positive()
                else:
                    print("Please enter a correct Testcase (solve call unsatisfiable)")
                    return 0
            elif loop == "scc":
                if not self.graph:
                    self.graph = build_dependency_graph(self.rules)
                if not self.sccs:
                    self.sccs = find_sccs(self.graph)
                self.add_sccs(self.ctl)
                self.ctl.ground([("base", [])])
                res = self.ctl.solve(on_model=self.on_model)
                if res.satisfiable:
                    self.check_rule_negative()
                    self.check_definition_negative()
                    self.check_component_negative()
                    self.ctl.configuration.solve.enum_mode = "brave"
                    self.ctl.solve(on_model=self.on_model)
                    self.check_rule_positive()
                    self.check_definition_positive()
                    self.check_component_positive()
                else:
                    print("Please enter a correct Testcase (solve call unsatisfiable)")
                    return 0
            elif loop == "test":
                print(self.ctl.solve(on_model=print))
            else:
                self.ctl.configuration.solve.enum_mode = "cautious"
                res = self.ctl.solve(on_model=self.on_model)
                if res.satisfiable:
                    self.check_rule_negative()
                    self.check_definition_negative()
                    self.ctl.configuration.solve.enum_mode = "brave"
                    self.ctl.solve(on_model=self.on_model)
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

        positiveD = (len(self.posDCov)*100) / self.numDef
        negativeD = (len(self.negDCov)*100) / self.numDef
        print(f"\nPositive definition coverage: {positiveD}% ({len(self.posDCov)} out of {self.numDef} atoms)")
        print(f"Negative definition coverage: {negativeD}% ({len(self.negDCov)} out of {self.numDef} atoms)")
        if verbose and positiveD != 100.0:
            self.print_pos_Dcoverage()
        if verbose and negativeD != 100.0:
            self.print_neg_Dcoverage()

        if loop == "loop":
            positiveL = ((len(self.posLCov) + len(self.posDCov)) * 100) / (self.numDef + len(self.loops))
            negativeL = ((len(self.negLCov) + len(self.negDCov)) * 100) / (self.numDef + len(self.loops))
            print(f"\nPositive loop coverage: {positiveL}% ({len(self.posLCov) + len(self.posDCov)} out of {self.numDef + len(self.loops)} loops)")
            print(f"Negative loop coverage: {negativeL}% ({len(self.negLCov) + len(self.negDCov)} out of {self.numDef + len(self.loops)} loops)")
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
        print(self.posRCov)
        print(self.negRCov)
        print(self.posDCov)
        print(self.negDCov)   
        print(self.posLCov)
        print(self.negLCov)
        # print(self.heads) 
        # print(self.rules)    
        # print(self.loops)
        # print(self.sccs)
           

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
                locations[head].append(self.heads[head][1])

        print("\nAtoms that have not been positively definition-covered:")
        for atm, locs in locations.items():
            print(atm)
            for loc in locs[0]:
                print("line: {}, column: {}".format(loc.begin[1], loc.begin[2]))

    def print_neg_Dcoverage(self):
        locations = defaultdict(list)
        for head in self.heads:
            if head not in self.negDCov:
                locations[head].append(self.heads[head][1])

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
                    locations[loop].append(self.heads[(atm.atom.symbol.name,len(atm.atom.symbol.arguments))][1])

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
                    locations[loop].append(self.heads[(atm.atom.symbol.name,len(atm.atom.symbol.arguments))][1])

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
                    locations[tuple(scc)].append(self.heads[(atm.atom.symbol.name,len(atm.atom.symbol.arguments))][1])

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
                    locations[tuple(scc)].append(self.heads[(atm.atom.symbol.name,len(atm.atom.symbol.arguments))][1])

        print("\nComponents that have not been negatively component-covered:")
        for scc, locs in locations.items():
            print([atm.atom.symbol.name for atm in scc])
            for i in range(len(scc)):
                print(scc[i].atom.symbol.name)
                for j in range(len(locs[i])):
                    print("line: {}, column: {}".format(locs[i][j].begin[1], locs[i][j].begin[2]))