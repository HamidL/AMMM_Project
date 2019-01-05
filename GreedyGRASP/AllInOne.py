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

    print()
    print()
    print()
    print('Problem settings:')
    print("Services: " + str(problem.inputData.nServices) + " Drivers: " + str(
        problem.inputData.nDrivers) + " Buses: " + str(problem.inputData.nBuses))
    config.localSearch = False
    print("LocalSearch: " + str(config.localSearch))
    if (config.localSearch):
        print(
            "Solver: " + config.solver + " Neighborhood Strategy: " + config.neighborhoodStrategy + " Policy: " + config.policy)
    if (config.solver == 'Greedy'):
        solver = Solver_Greedy()
        solution = solver.solve(config, problem)
    elif (config.solver == 'GRASP'):
        solver = Solver_GRASP()
        solution = solver.solve(config, problem)
    print()
    print()
    print()
    config.localSearch = True
    for neighborhoodStrategy in [ "Reassignment" , "Exchange"]:
        config.neighborhoodStrategy = neighborhoodStrategy
        for policy in ["BestImprovement" , "FirstImprovement"]:
            config.policy = policy
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
            print()
            print()
            print()

    return 0


if __name__ == '__main__':
    sys.exit(run())
