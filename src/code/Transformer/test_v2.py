import sys, time
# from CoverageCheck_v3 import CoverageCheck
from CoverageCheck_v4 import CoverageCheck
# from transformer_test import CoverageCheck
from dependencygraph_tools import find_loops

def main():
    testcases = sys.argv[2:]
    program = sys.argv[1]

    check = CoverageCheck()
    start = time.time()
    check.check_coverage(program, testcases)
    print("\nComputationtime: {}".format(time.time()-start))

if __name__ == "__main__":
    main()