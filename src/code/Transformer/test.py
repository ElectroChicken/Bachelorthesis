import sys, time
from CoverageCheck import CoverageCheck
# from transformer_test import CoverageCheck
from dependencygraph_tools import find_loops

def main():
    testcases = sys.argv[2:]
    program = sys.argv[1]

    check = CoverageCheck()
    start = time.time()
    check.check_coverage(program, testcases)
    # loops = find_loops([[1,2,3],range(5)])
    # print(loops)
    print("Computationtime: {}".format(time.time()-start))

if __name__ == "__main__":
    main()