from clingo.application import Application, clingo_main
from distutils.command import build
from email import message
from clingo.ast import ProgramBuilder, parse_files, parse_string, ASTType
from clingo.control import Control
from clingo import ast
from collections import defaultdict
import networkx as nx
from RuleTagger_v5 import RuleTagger
from dependencygraph_tools import build_dependency_graph, find_sccs, find_loops

class CoverageCheck(Application):
    def __init__(self, args, ipt):
        self.posRCov = set()
        self.maxPosRCov = set()
        self.negRCov = set()
        self.maxNegRCov = set()
        self.posDCov = set()
        self.maxPosDCov = set()
        self.negDCov = set()
        self.maxNegDCov = set()
        self.posLCov = set()
        self.maxPosLCov = set()
        self.negLCov = set()
        self.maxNegLCov = set()
        self.posCCov = set()
        self.maxPosCCov = set()
        self.negCCov = set()   
        self.maxNegCCov = set()     
        self.numRules = 0
        self.numDef = 0
        self.numTestcases = 0
        self.numModels = 0
        self.rules = []
        self.heads = dict()
        self.loops = set()
        self.sccs = []
        self.graph = nx.DiGraph()
        self.args = args
        self.ipt = ipt.replace(",",";")
        # self.ctl = Control(["0"], message_limit=0)
        self.program_name = "CoverageCheck"
    

    def main(self, ctl, files):
        pass

    def on_model(self, model):
        self.atoms = set([atm.name for atm in model.symbols(atoms=True) if atm.name.startswith("_")])
        # print(model)


    def add_rules(self):
        with ProgramBuilder(self.ctl) as bld:
            for idx, rule in enumerate(self.rules):
                    pos = ast.Position('<string>', 1, 1)
                    loc = ast.Location(pos, pos)
                    fun = ast.Function(loc, '_r{}'.format(idx), [], False)
                    atm = ast.SymbolicAtom(fun)
                    lit = ast.Literal(loc, ast.Sign.NoSign, atm)
                    bld.add(ast.Rule(loc, lit, rule.body))
                    print(ast.Rule(loc, lit, rule.body))

    def add_definitions(self):
        with ProgramBuilder(self.ctl) as bld:
            for value in self.heads.values():
                    for idx in value[2]:
                        pos = ast.Position('<string>', 1, 1)
                        loc = ast.Location(pos, pos)
                        fun = ast.Function(loc, '_d{}'.format(value[0][0]), [], False)
                        atm = ast.SymbolicAtom(fun)
                        head = ast.Literal(loc, ast.Sign.NoSign, atm)
                        fun2 = ast.Function(loc, '_r{}'.format(idx), [], False)
                        atm2 = ast.SymbolicAtom(fun2)
                        body = ast.Literal(loc, ast.Sign.NoSign, atm2)
                        bld.add(ast.Rule(loc, head, [body]))
                        print(ast.Rule(loc, head, [body]))

    def add_loops(self):
        with ProgramBuilder(self.ctl) as bld:
            for idx, loop in enumerate(self.loops):
                body = []
                pos = ast.Position('<string>', 1, 1)
                loc = ast.Location(pos, pos)
                fun = ast.Function(loc, '_l{}'.format(idx), [], False)
                atm = ast.SymbolicAtom(fun)
                head = ast.Literal(loc, ast.Sign.NoSign, atm)
                for key in loop:
                    fun = ast.Function(loc, '_d{}'.format(self.heads[key][0][0]), [], False)
                    atm = ast.SymbolicAtom(fun)
                    lit = ast.Literal(loc, ast.Sign.NoSign, atm)
                    body.append(lit)
                bld.add(ast.Rule(loc, head, body))
                print(ast.Rule(loc, head, body))
            
    def add_sccs(self):
        with ProgramBuilder(self.ctl) as bld:
            for idx, scc in enumerate(self.sccs):
                body = []
                pos = ast.Position('<string>', 1, 1)
                loc = ast.Location(pos, pos)
                fun = ast.Function(loc, '_s{}'.format(idx), [], False)
                atm = ast.SymbolicAtom(fun)
                head = ast.Literal(loc, ast.Sign.NoSign, atm)
                for key in scc:
                    fun = ast.Function(loc, '_d{}'.format(self.heads[key][0][0]), [], False)
                    atm = ast.SymbolicAtom(fun)
                    lit = ast.Literal(loc, ast.Sign.NoSign, atm)
                    body.append(lit)
                bld.add(ast.Rule(loc, head, body))
                print(ast.Rule(loc, head, body))

    def add_input(self, node):
        if not node.ast_type == ASTType.Program:
            pos = ast.Position('<string>', 1, 1)
            loc = ast.Location(pos, pos)
            fun = ast.Function(loc, '_i{}'.format(self.numTestcases), [], False)
            atm = ast.SymbolicAtom(fun)
            body = ast.Literal(loc, ast.Sign.NoSign, atm)
            with ProgramBuilder(self.ctl) as bld:
                bld.add(ast.Rule(loc, node.head, [body]))
                print(ast.Rule(loc, node.head, [body]))

    def add_program(self):
        if self.args.rule or self.args.definition or self.args.loop or self.args.component:
            for file in self.args.testcases:
                parse_files([file], self.add_input)
                self.numTestcases += 1
            with ProgramBuilder(self.ctl) as bld:
                str = "{ " + " ".join([f"_i{num};" for num in range(self.numTestcases)])[:-1] + " } = 1."
                parse_string(str, bld.add)
                parse_files(self.args.program, lambda stm: bld.add(self.gather_info(stm)))
                self.numRules = len(self.rules)
            
        
    def gather_info(self, node):
        if not node.ast_type == ASTType.Program:
            self.rules.append(node)
            print(node)
            if str(node.head) != "#false":
                if node.head.ast_type == ASTType.Aggregate or node.head.ast_type == ASTType.Disjunction:
                    for elem in node.head.elements:
                        key = (elem.literal.atom.symbol.name, len(elem.literal.atom.symbol.arguments))
                        if key not in self.heads.keys():
                            self.heads[key] = [[self.numDef],[elem.literal.location],[len(self.rules)-1]]
                            self.numDef += 1
                        else:
                            if not self.heads[key][2]:
                                self.heads[key][1] = []
                            self.heads[key][1].append(elem.literal.location)
                            self.heads[key][2].append(len(self.rules)-1)
                elif node.head.ast_type == ASTType.Literal:
                    key = (node.head.atom.symbol.name, len(node.head.atom.symbol.arguments))
                    if key not in self.heads.keys():
                        self.heads[key] = [[self.numDef],[node.head.location],[len(self.rules)-1]]
                        self.numDef += 1
                    else:
                        if not self.heads[key][2]:
                            self.heads[key][1] = []
                        self.heads[key][1].append(node.head.location)
                        self.heads[key][2].append(len(self.rules)-1)
                for atm in node.body:
                    key = (atm.atom.symbol.name, len(atm.atom.symbol.arguments))
                    if key not in self.heads.keys():
                        self.heads[key] = [[self.numDef],[atm.location],[]]
                        self.numDef += 1
            else:
                for atm in node.body:
                    key = (atm.atom.symbol.name, len(atm.atom.symbol.arguments))
                    if key not in self.heads.keys():
                        self.heads[key] = [[self.numDef],[atm.location],[]]
                        self.numDef += 1
                pos = ast.Position('<string>', 1, 1)
                loc = ast.Location(pos, pos)
                fun = ast.Function(loc, '_c', [], False)
                atm = ast.SymbolicAtom(fun)
                lit = ast.Literal(loc, ast.Sign.NoSign, atm)
                return node.update(head=lit)
        return node


    def setup(self):
        self.add_program()
        if self.args.rule or self.args.definition or self.args.loop or self.args.component:
            self.add_rules()
            
        if self.args.definition or self.args.loop or self.args.component:
            self.add_definitions()
            
        if self.args.loop or self.args.component:
            self.graph = build_dependency_graph(self.rules, self.heads)
            self.sccs = find_sccs(self.graph)

        if self.args.loop:
            self.loops = find_loops(self.graph, self.sccs)
            self.add_loops()

        if self.args.component:
            self.add_sccs()


    def check_rule_positive(self, max=False):
        if max:
            self.maxPosRCov.update(set([label for label in self.atoms if label.startswith("_r")]))
        else:
            self.posRCov.update(set([label for label in self.atoms if label.startswith("_r")]))

    def check_rule_negative(self, max=False):
        for i in range(self.numRules):
            if "_r"+str(i) not in self.atoms:
                if max:
                    self.maxNegRCov.add("_r"+str(i))
                else:
                    self.negRCov.add("_r"+str(i))

    def check_definition_positive(self, max=False):
        if max:
            self.maxPosDCov.update(set([label for label in self.atoms if label.startswith("_d")]))
        else:
            self.posDCov.update(set([label for label in self.atoms if label.startswith("_d")]))

    def check_definition_negative(self, max=False):
        for i in range(self.numDef):
            if "_d"+str(i) not in self.atoms:
                if max:
                    self.maxNegDCov.add("_d"+str(i))
                else:
                    self.negDCov.add("_d"+str(i))

    def check_component_positive(self, max=False):
        if max:
            self.maxPosCCov.update(set([label for label in self.atoms if label.startswith("_s")]))
        else:
            self.posCCov.update(set([label for label in self.atoms if label.startswith("_s")]))

    def check_component_negative(self, max=False):
        for i in range(len(self.sccs)):
            if "_s"+str(i) not in self.atoms:
                if max:
                    self.maxNegCCov.add("_s"+str(i))
                else:
                    self.negCCov.add("_s"+str(i))

    def check_loop_positive(self, max=False):
        if max:
            self.maxPosLCov.update(set([label for label in self.atoms if label.startswith("_l")]))
        else:
            self.posLCov.update(set([label for label in self.atoms if label.startswith("_l")]))

    def check_loop_negative(self, max=False):
        for i in range(len(self.loops)):
            if "_l"+str(i) not in self.atoms:
                if max:
                    self.maxNegLCov.add("_l"+str(i))
                else:
                    self.negLCov.add("_l"+str(i))

    def check_possible_coverage(self):
        self.ctl = Control(["0"], message_limit=0)

        with ProgramBuilder(self.ctl) as bld:
            parse_files(self.args.program, bld.add)
            str = "{ " + self.ipt + " }."
            parse_string(str, bld.add)
        self.ctl.ground([("base", [])])
        self.ctl.configuration.solve.enum_mode = "brave"
        self.ctl.solve(on_model=self.on_model)
        if self.args.rule:
            self.check_rule_positive(max=True)
        if self.args.definition or self.args.loop:
            self.check_definition_positive(max=True)
        if self.args.loop:
            self.check_loop_positive(max=True)
        if self.args.component:
            self.check_component_positive(max=True)
        self.ctl.configuration.solve.enum_mode = "cautious"
        self.ctl.solve(on_model=self.on_model)
        if self.args.rule:
            self.check_rule_negative(max=True)
        if self.args.definition or self.args.loop:
            self.check_definition_negative(max=True)
        if self.args.loop:
            self.check_loop_negative(max=True)
        if self.args.component:
            self.check_component_negative(max=True)

    def check_coverage(self):
        if self.args.rule or self.args.definition or self.args.loop or self.args.component:
            self.ctl.configuration.solve.enum_mode = "brave"
            self.ctl.ground([("base", [])])
            res = self.ctl.solve(on_model=self.on_model)
            if res.satisfiable:
                if self.args.rule:
                    self.check_rule_positive()
                if self.args.definition or self.args.loop:
                    self.check_definition_positive()
                if self.args.loop:
                    self.check_loop_positive()
                if self.args.component:
                    self.check_component_positive()
                self.ctl.configuration.solve.enum_mode = "cautious"
                self.ctl.solve(on_model=self.on_model)
                if self.args.rule:
                    self.check_rule_negative()
                if self.args.definition or self.args.loop:
                    self.check_definition_negative()
                if self.args.loop:
                    self.check_loop_negative()
                if self.args.component:
                    self.check_component_negative()
                # self.check_possible_coverage()
            else:
                print("Please enter a correct Testcase (solve call unsatisfiable)")
                return 0
        if self.args.program:
            self.program_coverage()

        # for loop in self.loops:
        #     print([atm.atom.symbol.name for atm in loop])
        # for scc in self.sccs:
        #     print([atm.atom.symbol.name for atm in scc])
        # print(self.posRCov)
        # print(self.negRCov)
        # print(self.posDCov)
        # print(self.negDCov)   
        # print(self.posLCov)
        # print(self.negLCov)
        # print(self.heads) 
        # print(self.rules)    
        # print(self.loops)
        # print(self.sccs)
           
    def print_coverage(self):

        if self.args.rule:
            positiveR = (len(self.posRCov)*100) / self.numRules
            negativeR = (len(self.negRCov)*100) / self.numRules
            print(f"\nPositive rule coverage: {positiveR:.3g}% ({len(self.posRCov)} out of {self.numRules} rules)")
            print(f"Negative rule coverage: {negativeR:.3g}% ({len(self.negRCov)} out of {self.numRules} rules)")
            if self.args.verbose:
                if positiveR != 100:
                    self.print_pos_Rcoverage()
                if negativeR != 100:
                    self.print_neg_Rcoverage()

        if self.args.definition:
            positiveD = (len(self.posDCov)*100) / self.numDef
            negativeD = (len(self.negDCov)*100) / self.numDef
            print(f"\nPositive definition coverage: {positiveD:.3g}% ({len(self.posDCov)} out of {self.numDef} atoms)")
            print(f"Negative definition coverage: {negativeD:.3g}% ({len(self.negDCov)} out of {self.numDef} atoms)")
            if self.args.verbose:
                if positiveD != 100:
                    self.print_pos_Dcoverage()
                if negativeD != 100:
                    self.print_neg_Dcoverage()

        if self.args.loop:
            positiveL = ((len(self.posLCov) + len(self.posDCov)) * 100) / (self.numDef + len(self.loops))
            negativeL = ((len(self.negLCov) + len(self.negDCov)) * 100) / (self.numDef + len(self.loops))
            print(f"\nPositive loop coverage: {positiveL:.3g}% ({len(self.posLCov) + len(self.posDCov)} out of {self.numDef + len(self.loops)} loops)")
            print(f"Negative loop coverage: {negativeL:.3g}% ({len(self.negLCov) + len(self.negDCov)} out of {self.numDef + len(self.loops)} loops)")
            if self.args.verbose:
                if positiveL != 100:
                    self.print_pos_Lcoverage()
                if negativeL != 100:
                    self.print_neg_Lcoverage()

        if self.args.component:
            positiveC = (len(self.posCCov) * 100) / (len(self.sccs))
            negativeC = (len(self.negCCov) * 100) / (len(self.sccs))
            print(f"\nPositive component coverage: {positiveC:.3g}% ({len(self.posCCov)} out of {len(self.sccs)} components)")
            print(f"Negative component coverage: {negativeC:.3g}% ({len(self.negCCov)} out of {len(self.sccs)} components)")
            if self.args.verbose:
                if positiveC != 100:
                    self.print_pos_Ccoverage()
                if negativeC != 100:
                    self.print_neg_Ccoverage()


    def print_pos_Rcoverage(self):
        cov = [int(label[2:]) for label in self.posRCov]
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
        cov = [int(label[2:]) for label in self.posDCov]

        print("\nAtoms that have not been positively definition-covered:")
        for idx, (atm, values) in enumerate(self.heads.items()):
            if idx not in cov:
                print(atm)
                for loc in values[1]:
                    print("line: {}, column: {}".format(loc.begin[1], loc.begin[2]))

    def print_neg_Dcoverage(self):
        cov = [int(label[2:]) for label in self.negDCov]

        print("\nAtoms that have not been negatively definition-covered:")
        for idx, (atm, values) in enumerate(self.heads.items()):
            if idx not in cov:
                print(atm)
                for loc in values[1]:
                    print("line: {}, column: {}".format(loc.begin[1], loc.begin[2]))

    def print_pos_Lcoverage(self):
        cov = [int(label[2:]) for label in self.posLCov]

        print("\nLoops that have not been positively loop-covered:", end='')
        for idx, loop in enumerate(self.loops):
            if idx not in cov:
                print("\n", [atm[0] for atm in loop], sep='')
                for atm in loop:
                    print(atm)
                    locs = self.heads[atm][1]
                    for j in range(len(locs)):
                        print("line: {}, column: {}".format(locs[j].begin[1], locs[j].begin[2]))
        
        cov = [int(label[2:]) for label in self.posDCov]
        for idx, (atm, values) in enumerate(self.heads.items()):
            if idx not in cov:
                print("\n", list(atm[0]), sep='')
                print(atm)
                for loc in values[1]:
                    print("line: {}, column: {}".format(loc.begin[1], loc.begin[2]))

    def print_neg_Lcoverage(self):
        cov = [int(label[2:]) for label in self.negLCov]

        print("\nLoops that have not been negatively loop-covered:", end='')
        for idx, loop in enumerate(self.loops):
            if idx not in cov:
                print("\n", [atm[0] for atm in loop], sep='')
                for atm in loop:
                    print(atm)
                    locs = self.heads[atm][1]
                    for j in range(len(locs)):
                        print("line: {}, column: {}".format(locs[j].begin[1], locs[j].begin[2]))

        cov = [int(label[2:]) for label in self.negDCov]
        for idx, (atm, values) in enumerate(self.heads.items()):
            if idx not in cov:
                print('\n', list(atm[0]), sep='')
                print(atm)
                for loc in values[1]:
                    print("line: {}, column: {}".format(loc.begin[1], loc.begin[2]))

    def print_pos_Ccoverage(self):
        cov = [int(label[2:]) for label in self.posCCov]

        print("\nComponents that have not been positively component-covered:", end='')
        for idx, scc in enumerate(self.sccs):
            if idx not in cov:
                print("\n", [atm[0] for atm in scc], sep='')
                for atm in scc:
                    print(atm)
                    locs = self.heads[atm][1]
                    for j in range(len(locs)):
                        print("line: {}, column: {}".format(locs[j].begin[1], locs[j].begin[2]))

    def print_neg_Ccoverage(self):
        cov = [int(label[2:]) for label in self.negCCov]

        print("\nComponents that have not been negatively component-covered:", end='')
        for idx, scc in enumerate(self.sccs):
            if idx not in cov:
                print("\n", [atm[0] for atm in scc], sep='')
                for atm in scc:
                    print(atm)
                    locs = self.heads[atm][1]
                    for j in range(len(locs)):
                        print("line: {}, column: {}".format(locs[j].begin[1], locs[j].begin[2]))


    def program_coverage(self):
        self.ctl = Control(["0"], message_limit=0)

        with ProgramBuilder(self.ctl) as bld:
            parse_files(self.args.program, bld.add)
            str = "{ " + self.ipt + " }."
            parse_string(str, bld.add)
        self.ctl.ground([("base", [])])
        self.ctl.solve(on_model=self.count_models)
        max = self.numModels

        self.ctl = Control(["0"], message_limit=0)
        for file in self.args.testcases:
            parse_files([file], self.add_input)
            self.numTestcases += 1
        with ProgramBuilder(self.ctl) as bld:
            str = "{ " + " ".join([f"_i{num};" for num in range(self.numTestcases)])[:-1] + " } = 1."
            parse_string(str, bld.add)
            parse_files(self.args.program, bld.add)
        self.ctl.ground([("base", [])])
        self.ctl.solve(on_model=self.count_models)
        num = self.numModels



    def count_models(self, model):
        self.numModels = model.number