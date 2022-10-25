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

inputs = []
ctl = Control(["0"])
def main():
    testcases = sys.argv[1:]
    global numIn
    numIn = 0
    with ProgramBuilder(ctl) as bld:
        for file in testcases:
            inputs.clear()
            parse_files([file], test)
            numIn += 1
        str = ' '.join([f"_i{i};" for i in range(numIn)])
        parse_string("{ "+str[:-1]+" } = 1.", bld.add)
    ctl.ground([('base', [])])
    print(ctl.solve(on_model=print))

def test(rule):
    # print(ast.values())
    if not rule.ast_type == ASTType.Program:
        # inputs.append(ast.head)
        pos = ast.Position('<string>', 1, 1)
        loc = ast.Location(pos, pos)
        fun = ast.Function(loc, '_i{}'.format(numIn), [], False)
        atm = ast.SymbolicAtom(fun)
        body = ast.Literal(loc, ast.Sign.NoSign, atm)
        with ProgramBuilder(ctl) as bld:
            bld.add(ast.Rule(loc, rule.head, [body]))
        
    # print(inputs)

if __name__ == "__main__":
    main()