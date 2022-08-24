import sys
from clingo.application import Application, clingo_main
from clingo.ast import ProgramBuilder, parse_string
from clingo.control import Control

class Coverage_check(Application):
    program_name = "coverage_check"
    version = "1.0"

    def __init__(self):
        self.inputAtoms = set()

    def _on_model(self, model):
        for atom in model.symbols(atoms=True):
            print(atom)

    def logger(self, code, message):
        #print("code: " + str(code))
        #print("message: " + message)

        if (str(code) == "MessageCode.AtomUndefined"):
            self.inputAtoms.add(message[-2])
        #print(self.inputAtoms)
        

    def main(self, ctl, files):
        for path in files:
            ctl.load(path)
        if not files:
            ctl.load("-")
        ctl.configuration.solve.models = 0
        ctl.ground([("base", [])])
        with ProgramBuilder(ctl) as bld:
            for var in self.inputAtoms:
                parse_string("#external {}.".format(var), bld.add)
                #print(var)
        ctl.ground([("base", [])])
        ctl.symbolic_atoms
        
        #ctl.solve()

if __name__ == "__main__":
    clingo_main(Coverage_check(), sys.argv[1:])