from ast import AST
from clingo.control import Control
from clingo.symbol import Function, Number, parse_term
from clingo.ast import Transformer, ProgramBuilder, parse_files, parse_string, ASTType
from clingo import ast
import sys

# class Trans(Transformer):
#     def __init__(self):
#         self.rules = []

#     def visit_Rule(self, node):
#         self.rules.append(node)
#         return node

# class test:
#     def __init__(self):
#         self.n = 0
#         self.atoms = ["a(2)", "b(1)", "c(3)"]

#     def run(self):
#         ctl = Control(["0"])
#         trans = Trans()
#         with ProgramBuilder(ctl) as bld:
#             parse_files(["p2.lp"], lambda stm: bld.add(trans(stm)))
#         ctl.ground([("base", [])])
#         # for i in range(len(self.atoms)):
#         #     ctl.assign_external(parse_term(self.atoms[i]), True)
#         #     print(ctl.solve(on_model=print))
#         #     ctl.assign_external(parse_term(self.atoms[i]), False)
#         print(trans.rules)
#         for rule in trans.rules:
#             print(rule.head.ast_type)
#         print(ctl.solve(on_model=print))

#     # def testcase(self, n):
#     #     # fun = Function("a", [n])
#     #     return parse_term(self.atoms[n.number])

# def main():
#     t = test()
#     t.run()

# if __name__ == "__main__":
#     main()

# # import sys, time
# # # from CoverageCheck_v2 import CoverageCheck
# # from Transformer.CoverageCheck_v3 import CoverageCheck
# # # from transformer_test import CoverageCheck
# # from Transformer.dependencygraph_tools import find_loops

# # def main():
# #     testcases = sys.argv[2:]
# #     program = sys.argv[1]

# #     check = CoverageCheck()
# #     start = time.time()
# #     check.check_coverage(program, testcases)
# #     print("\nComputationtime: {}".format(time.time()-start))

atms = set()
ctl = Control(["0"])
def main():
    prog = sys.argv[1]
    # with ProgramBuilder(ctl) as bld:
        # parse_files([prog], lambda stm: bld.add(test2(stm)))
        # parse_string("#false.", lambda stm: bld.add(test2(stm)))
    parse_files([prog], prints)
    # print(sorted(atms))
    # ctl.ground([('base', [])])
    # print(ctl.solve(on_model=print))

def prints(node):
    if node.ast_type != ASTType.Program:
        print(node)
        print(node.ast_type)
        # print(node.items())

def test2(node):
    if node.ast_type != ASTType.Program:
        if node.ast_type == ASTType.ShowSignature or node.ast_type == ASTType.ShowTerm:
            print(node)
            pos = ast.Position('<string>', 1, 1)
            loc = ast.Location(pos, pos)
            atm = ast.BooleanConstant(1)
            lit = ast.Literal(loc, ast.Sign.NoSign, atm)
            return ast.Rule(loc, lit, [])
        elif str(node.head) == "#false":
            print(node)
            pos = ast.Position('<string>', 1, 1)
            loc = ast.Location(pos, pos)
            atm = ast.BooleanConstant(1)
            lit = ast.Literal(loc, ast.Sign.NoSign, atm)
            return ast.Rule(loc, lit, [])
    return node

def test(node):
    if node.ast_type == ASTType.Rule:
        # print(node.head.atom.symbol)
        print(node.head)
        print(node.head.ast_type)
        print(node.head.elements)
        print(node.head.elements[0].condition)
        # print(node.head.atom.symbol.ast_type)
        # print(node.head.atom.symbol.keys())
        ### Body ###
        for atm in node.body:
            if atm.ast_type == ASTType.Literal:
                if atm.atom.ast_type == ASTType.SymbolicAtom:
                    if atm.atom.symbol.ast_type == ASTType.Pool:
                        key = (atm.atom.symbol.arguments[0].name, len(atm.atom.symbol.arguments[0].arguments))
                    else:
                        key = (atm.atom.symbol.name, len(atm.atom.symbol.arguments))
                    atms.add((key[0], key[1],"n"))
                elif atm.atom.ast_type == ASTType.Aggregate or atm.atom.ast_type == ASTType.BodyAggregate:
                    pass
            elif atm.ast_type == ASTType.ConditionalLiteral:
                atms.add((atm.literal.atom.symbol.name, len(atm.literal.atom.symbol.arguments),"n"))
                for lit in atm.condition:
                    if lit.atom.ast_type == ASTType.SymbolicAtom:
                        atms.add((lit.atom.symbol.name, len(lit.atom.symbol.arguments),"n"))
                    elif lit.atom.ast_type == ASTType.Aggregate or lit.atom.ast_type == ASTType.BodyAggregate:
                        pass

        ### Head ###            
        if node.head.ast_type == ASTType.Literal:
            if node.head.atom.ast_type == ASTType.SymbolicAtom:
                if node.head.atom.symbol.ast_type == ASTType.Pool:
                    key = (node.head.atom.symbol.arguments[0].name, len(node.head.atom.symbol.arguments[0].arguments))
                else:
                    key = (node.head.atom.symbol.name, len(node.head.atom.symbol.arguments))
                atms.add(key)
        elif node.head.ast_type == ASTType.Aggregate or node.head.ast_type == ASTType.Disjunction:
            for elem in node.head.elements:
                if elem.literal.atom.ast_type == ASTType.SymbolicAtom:
                    atms.add((elem.literal.atom.symbol.name, len(elem.literal.atom.symbol.arguments)))
                for lit in elem.condition:
                    if lit.atom.ast_type == ASTType.SymbolicAtom:
                        atms.add((lit.atom.symbol.name, len(lit.atom.symbol.arguments), "n"))    # dont set the rule here since it is not defined here
        elif node.head.ast_type == ASTType.HeadAggregate:
            for elem in node.head.elements:
                if elem.condition.literal.atom.ast_type == ASTType.SymbolicAtom:
                    atms.add((elem.condition.literal.atom.symbol.name, len(elem.condition.literal.atom.symbol.arguments)))
                for lit in elem.condition.condition:
                    if lit.atom.ast_type == ASTType.SymbolicAtom:
                        atms.add((lit.atom.symbol.name, len(lit.atom.symbol.arguments),"n"))    # dont set the rule here since it is not defined here
    
    if node.ast_type == ASTType.ShowSignature or node.ast_type == ASTType.ShowTerm:
        pos = ast.Position('<string>', 1, 1)
        loc = ast.Location(pos, pos)
        fun = ast.Function(loc, '_z', [], False)
        atm = ast.SymbolicAtom(fun)
        lit = ast.Literal(loc, ast.Sign.NoSign, atm)
        return ast.Rule(loc, lit, [])
    return node           

        # print(node.head)
        # print(node.head.ast_type)
        # print(node.head.keys())
    # print(node.items())
    # if not rule.ast_type == ASTType.Program:
    #     # inputs.append(ast.head)
    #     pos = ast.Position('<string>', 1, 1)
    #     loc = ast.Location(pos, pos)
    #     fun = ast.Function(loc, '_i{}'.format(numIn), [], False)
    #     atm = ast.SymbolicAtom(fun)
    #     body = ast.Literal(loc, ast.Sign.NoSign, atm)
    #     with ProgramBuilder(ctl) as bld:
    #         bld.add(ast.Rule(loc, rule.head, [body]))
        
    # print(inputs)

if __name__ == "__main__":
    main()