
import argparse
import sys

from DATParser import DATParser
from ValidateInputData import ValidateInputData
from ValidateConfig import ValidateConfig
from Solver_Greedy import Solver_Greedy
#from Solver_GRASP import Solver_GRASP
from Problem import Problem
from Solution import Solution

def run():
    #try:
    print ('AMMM Project')
    print ('-------------------')

    print ('Reading Config file...')
    config = DATParser.parse('./config/config.dat')
    ValidateConfig.validate(config)

    print ('Reading Input Data file %s...' % config.inputDataFile)
    inputData = DATParser.parse(config.inputDataFile)
    ValidateInputData.validate(inputData)

    print ('Creating Problem...')
    problem = Problem(inputData)

    solver = Solver_Greedy()
    solution = solver.solve(config, problem)
    print(problem.OV)
    print(solution.driver_to_services)
    print(solution.bus_to_services)
    print(solution.worked_minutes)
    # if(problem.checkInstance()):
    #     print 'Solving Problem...'
    #     solver = None
    #     solution = None
    #     if(config.solver == 'Greedy'):
    #         solver = Solver_Greedy()
    #         solution = solver.solve(config, problem)
    #     elif(config.solver == 'GRASP'):
    #         solver = Solver_GRASP()
    #         solution = solver.solve(config, problem)
    #
    #     solution.saveToFile(config.solutionFile)
    # else:
    #     print 'Instance is infeasible.'
    #     solution = Solution.createEmptySolution(config, problem)
    #     solution.makeInfeasible()
    #     solution.saveToFile(config.solutionFile)

    return 0
    # except Exception as e:
    #     print()
    #     print('Exception:', e)
    #     print()
    #     return 1

if __name__ == '__main__':
    sys.exit(run())
