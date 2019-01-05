import sys

from GreedyGRASP.DATParser import DATParser
from GreedyGRASP.ValidateInputData import ValidateInputData
from GreedyGRASP.ValidateConfig import ValidateConfig
from GreedyGRASP.Solver_Greedy import Solver_Greedy
from GreedyGRASP.Solver_GRASP import Solver_GRASP
from GreedyGRASP.Problem import Problem


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
    print('Problem settings:')
    print("Services: " + str(problem.inputData.nServices) + " Drivers: " + str(problem.inputData.nDrivers) + " Buses: " + str(problem.inputData.nBuses))

    if(config.localSearch):
        print("Solver: " + config.solver + " Neighborhood Strategy: " + config.neighborhoodStrategy + " Policy: " + config.policy)
    if (config.solver == 'Greedy'):
        solver = Solver_Greedy()
        solution = solver.solve(config, problem)
    elif (config.solver == 'GRASP'):
        solver = Solver_GRASP()
        solution = solver.solve(config, problem)
    # print(problem.OV)
    # print(solution.driver_to_services)
    # print(solution.bus_to_services)
    # print(solution.worked_minutes)
    # print(problem.getServices()[102].getMinutes())
    # print(solution.cost)
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
