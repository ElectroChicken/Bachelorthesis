import sys
from clingo.application import Application, clingo_main
from clingo.ast import ProgramBuilder, parse_string
from clingo.control import Control

rules = []

class Observer:
    def rule(self, choice, head, body):
        rules.append([choice, head, body])
        print("rule:", choice, head, body)

    def external(self, atom, value):
        print("added external:", atom, value)

class Api_test(Application):
    program_name = "api_test"
    version = "1.0"

    def __init__(self):
        self.inputAtoms = set()

    def logger(self, code, message):
        # print("code: " + str(code))
        # print("message: " + message)

        if (str(code) == "MessageCode.AtomUndefined"):
            self.inputAtoms.add(message[-2])
        #print(self.inputAtoms)
        

    def main(self, ctl, files):
        for path in files[:-1]:
            ctl.load(path)
        if not files:
            ctl.load("-")
        ctl.configuration.solve.models = 0
        ctl.register_observer(Observer())
        ctl.ground([("base", [])])
        with ProgramBuilder(ctl) as bld:
            for var in self.inputAtoms:
                parse_string("#external {}.".format(var), bld.add)
                #print(var)
        ctl.ground([("base", [])])
        
        ctl.load(files[-1])
        ctl.ground([("base", [])])
        ctl.solve()

if __name__ == "__main__":
    clingo_main(Api_test(), sys.argv[1:])