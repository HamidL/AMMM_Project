
from Solver import Solver
from Solution import Solution
from LocalSearch import LocalSearch

# Inherits from a parent abstract solver.
class Solver_Greedy(Solver):

    def greedyFunctionCost(self, solution, remainCap, busesAssignments):
        for busAssi in busesAssignments:
            bus = solution.getBuses()[busAssi.bus]
            service = solution.getServices()[busAssi.service]
            if (remainCap <= bus.getCapacity()):
                cost = busAssi.cost + busAssi.cost*(bus.getCapacity()-remainCap)/bus.getCapacity()
            else:
                cost = busAssi.cost + (busAssi.cost + service.getMinutes()*solution.inputData.CBM) * remainCap / bus.getCapacity()
            busAssi.greedyCost = cost
        return busesAssignments

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

            remainCap = service.getPassengers()
            selBuses = []
            while (remainCap > 0 and len(busesAssignments) > 0):
                busesAssignments = self.greedyFunctionCost(solution, remainCap, busesAssignments)
                busesAssignments = sorted(busesAssignments, key=lambda busAssi: busAssi.greedyCost)
                candidate = busesAssignments[0]
                if (candidate is None):
                    solution.makeInfeasible()
                    break
                selBuses.append(candidate)
                busesAssignments.remove(candidate)
                remainCap -= problem.getBuses()[candidate.bus].getCapacity()

            if (remainCap > 0):
                solution.makeInfeasible()
                break

            sortedDriversAssignments = sorted(driversAssignments, key=lambda driverAssi: driverAssi.cost)
            if (len(sortedDriversAssignments) < len(selBuses)):
                solution.makeInfeasible()
                break

            for i in range(0,len(selBuses)):
                solution.assign(sortedDriversAssignments[i], selBuses[i])

        return(solution, elapsedEvalTime, evaluatedCandidates)

    def solve(self, config, problem):
        self.startTimeMeasure()
        self.writeLogLine(float('infinity'), 0)
        
        solution, elapsedEvalTime, evaluatedCandidates = self.greedyConstruction(config, problem)
        self.writeLogLine((solution.cost), 1)

        localSearch = LocalSearch(config)
        solution = localSearch.run(solution)

        self.writeLogLine(solution.cost, 1)
        
        avg_evalTimePerCandidate = 0.0
        if (evaluatedCandidates != 0):
            avg_evalTimePerCandidate = 1000.0 * elapsedEvalTime / float(evaluatedCandidates)

        print ('')
        print ('Greedy Candidate Evaluation Performance:')
        print ('  Num. Candidates Eval.', evaluatedCandidates)
        print ('  Total Eval. Time     ', elapsedEvalTime, 's')
        print ('  Avg. Time / Candidate', avg_evalTimePerCandidate, 'ms')
        
        localSearch.printPerformance()
        
        return(solution)
