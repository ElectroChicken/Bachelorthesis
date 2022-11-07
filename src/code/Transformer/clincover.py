import sys, time
from CoverageCheck_final import CoverageCheck
import argparse

def main():
    parser = argparse.ArgumentParser(description="A Program to calculate different coverage metrics for propositional answer set programs")
    parser.add_argument("-p", "--program", action="store_true", help="check for program coverage")
    parser.add_argument("-r", "--rule", action="store_true", help="check for rule coverage")
    parser.add_argument("-d", "--definition", action="store_true", help="check for definition coverage")
    parser.add_argument("-l", "--loop", action="store_true", help="check for loop coverage")
    parser.add_argument("-c", "--component", action="store_true", help="check for component coverage")
    parser.add_argument("-v", "--verbose", action="store_true", help="display additional coverage information like locations")

    parser.add_argument("files", nargs="+", help="The program files")
    parser.add_argument("-t", "--testcases", nargs="+", required=True, help="The testcase files")
    args = parser.parse_args()
    if not (args.program or args.rule or args.definition or args.loop or args.component):
        parser.error("No coverage metric specified. Please add at least one coverage metric.")
    
    ipt = input("Please enter all inputatoms seperated by comma:\n")
    
    check = CoverageCheck(args, ipt)
    # start = time.time()
    # check.setup()
    # check.check_coverage()
    # check.print_coverage()
    check.full_check()
    # print("\nComputationtime: {}".format(time.time()-start))

if __name__ == "__main__":
    main()