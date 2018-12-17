
from Solver import Solver
from Solution import Solution
#from LocalSearch import LocalSearch

# Inherits from a parent abstract solver.
class Solver_Greedy(Solver):
    
    def greedyConstruction(self, config, problem):
        # get an empty solution for the problem
        solution = Solution.createEmptySolution(config, problem)
        
        # get tasks and sort them by their total required resources in descending order
        services = problem.getServices()
        sortedServices = sorted(services,
                                key=lambda service: (service.getPassengers(), service.getNumOverlappingServices()),
                                reverse=True)
        
        elapsedEvalTime = 0
        evaluatedCandidates = 0
        
        # for each task taken in sorted order
        for service in sortedServices:
            serviceId = service.getId()
            busesAssignments, driversAssignments = solution.findFeasibleAssignments(serviceId)

            sortedBusesAssignments = sorted(busesAssignments, key=lambda busAssi: busAssi.cost)

            sortedDriversAssignments = sorted(driversAssignments, key=lambda driverAssi: driverAssi.cost)

            # assign the current task to the CPU that resulted in a minimum highest load
            solution.assign(sortedDriversAssignments.driver, sortedBusesAssignments.bus, service.getId())

        return(solution, elapsedEvalTime, evaluatedCandidates)

    def solve(self, config, problem):
        self.startTimeMeasure()
        self.writeLogLine(float('infinity'), 0)
        
        solution, elapsedEvalTime, evaluatedCandidates = self.greedyConstruction(config, problem)
        self.writeLogLine(solution.getHighestLoad(), 1)

        localSearch = LocalSearch(config)
        solution = localSearch.run(solution)

        self.writeLogLine(solution.getHighestLoad(), 1)
        
        avg_evalTimePerCandidate = 0.0
        if (evaluatedCandidates != 0):
            avg_evalTimePerCandidate = 1000.0 * elapsedEvalTime / float(evaluatedCandidates)

        # print ''
        # print 'Greedy Candidate Evaluation Performance:'
        # print '  Num. Candidates Eval.', evaluatedCandidates
        # print '  Total Eval. Time     ', elapsedEvalTime, 's'
        # print '  Avg. Time / Candidate', avg_evalTimePerCandidate, 'ms'
        
        localSearch.printPerformance()
        
        return(solution)
