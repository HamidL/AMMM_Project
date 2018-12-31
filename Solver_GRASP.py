import random, time
from Solver import Solver
from Solution import Solution
from copy import deepcopy
from LocalSearch import LocalSearch


# Inherits from a parent abstract solver.
class Solver_GRASP(Solver):
    def selectCandidateB(self, config, sortedCL):
        if (len(sortedCL) == 0): return (None)

        # sort candidate assignments by highestLoad in ascending order

        # compute boundary highest load as a function of the minimum and maximum highest loads and the alpha parameter
        alpha = config.alpha
        minCost = sortedCL[0].greedyCost
        maxCost = sortedCL[-1].greedyCost
        boundaryCost = minCost + (maxCost - minCost) * alpha

        # find elements that fall into the RCL (those fulfilling: highestLoad < boundaryHighestLoad)
        maxIndex = 0
        for x in sortedCL:
            if (x.greedyCost > boundaryCost): break
            maxIndex += 1

        # create RCL and pick an element randomly
        rcl = sortedCL[0:maxIndex]  # pick first maxIndex elements starting from element 0
        if (len(rcl) == 0): return (None)
        return rcl  # pick an element from rcl at random

    def selectCandidateD(self, config, sortedCL):
        if (len(sortedCL) == 0): return (None)

        # sort candidate assignments by highestLoad in ascending order

        # compute boundary highest load as a function of the minimum and maximum highest loads and the alpha parameter
        alpha = config.alpha
        minCost = sortedCL[0].cost
        maxCost = sortedCL[-1].cost
        boundaryCost = minCost + (maxCost - minCost) * alpha

        # find elements that fall into the RCL (those fulfilling: highestLoad < boundaryHighestLoad)
        maxIndex = 0
        for x in sortedCL:
            if (x.cost > boundaryCost): break
            maxIndex += 1
        # create RCL and pick an element randomly
        rcl = sortedCL[0:maxIndex]  # pick first maxIndex elements starting from element 0
        if (len(rcl) == 0): return (None)
        return rcl  # pick an element from rcl at random

    def greedyFunctionCost(self, solution, remainCap, busesAssignments):
        costs = []
        for busAssi in busesAssignments:
            bus = solution.getBuses()[busAssi.bus]
            service = solution.getServices()[busAssi.service]
            if (remainCap <= bus.getCapacity()):
                cost = busAssi.cost + busAssi.cost*(bus.getCapacity()-remainCap)/bus.getCapacity()
            else:
                cost = busAssi.cost + (busAssi.cost + service.getMinutes()*solution.inputData.CBM) * remainCap / bus.getCapacity()
            busAssi.greedyCost = cost
            costs.append(cost)
        #print(sorted(costs,reverse=False))
        return busesAssignments

    def greedyRandomizedConstruction(self, config, problem):
        solution = Solution.createEmptySolution(config, problem)

        # get tasks and sort them by their total required resources in descending order
        services = problem.getServices()
        sortedServices = sorted(services,
                                key=lambda service: (service.getPassengers(), service.getNumOverlappingServices()),
                                reverse=True)


        iteration_elapsedEvalTime = 0
        iteration_evaluatedCandidates = 0

        # for each task taken in sorted order
        lenB = []
        lenD = []
        servicesIds = []
        for service in sortedServices:
            serviceId = service.getId()
            servicesIds.append(serviceId)
            busesAssignments, driversAssignments = solution.findFeasibleAssignments(serviceId)
            lenB.append(len(busesAssignments))
            lenD.append(len(driversAssignments))
            remainCap = service.getPassengers()
            selBuses = []
            while (remainCap > 0 and len(busesAssignments) > 0):
                busesAssignments = self.greedyFunctionCost(solution, remainCap, busesAssignments)
                busesAssignments = sorted(busesAssignments, key=lambda busAssi: busAssi.greedyCost)
                rcl = self.selectCandidateB(config, busesAssignments)
                if(rcl is None):
                    solution.makeInfeasible()
                    break

                candidate = random.choice(rcl)
                selBuses.append(candidate)
                busesAssignments.remove(candidate)
                remainCap -= problem.getBuses()[candidate.bus].getCapacity()
            if (remainCap > 0):
                solution.makeInfeasible()
                break

            if(not solution.isFeasible()):
                break

            sortedDriversAssignments = sorted(driversAssignments, key=lambda driverAssi: driverAssi.cost)
            selDrivers = []
            if(len(sortedDriversAssignments) < len(selBuses)):
                    solution.makeInfeasible()

            while (len(selDrivers) < len(selBuses)):
                rcl = self.selectCandidateD(config,sortedDriversAssignments)
                if(rcl is None):
                    solution.makeInfeasible()
                    break
                candidate = random.choice(rcl)
                selDrivers.append(candidate)
                sortedDriversAssignments.remove(candidate)

            if(not solution.isFeasible()):
                break

            for i in range(0, len(selDrivers)):
                solution.assign(selDrivers[i], selBuses[i])
        #print(len(rcl))
        return (solution, iteration_elapsedEvalTime, iteration_evaluatedCandidates)

    def solve(self, config, problem):
        bestSolution = Solution.createEmptySolution(config, problem)
        bestSolution.makeInfeasible()
        bestCost = bestSolution.cost
        self.startTimeMeasure()
        self.writeLogLine(bestCost, 0)

        total_elapsedEvalTime = 0
        total_evaluatedCandidates = 0

        localSearch = LocalSearch(config)

        iteration = 0
        while (time.time() - self.startTime < config.maxExecTime):
            iteration += 1

            # force first iteration as a Greedy execution (alpha == 0)
            originalAlpha = config.alpha
            if (iteration == 1): config.alpha = 0
            solution, it_elapsedEvalTime, it_evaluatedCandidates = self.greedyRandomizedConstruction(config, problem)

            total_elapsedEvalTime += it_elapsedEvalTime
            total_evaluatedCandidates += it_evaluatedCandidates

            # recover original alpha
            if (iteration == 1): config.alpha = originalAlpha

            if (not solution.isFeasible()):
                continue

            solution = localSearch.run(solution)

            solutionCost = solution.cost
            if (solutionCost < bestCost):
                bestSolution = solution
                bestCost = solutionCost
                self.writeLogLine(bestCost, iteration)
            # print(solutionCost, bestCost)
        self.writeLogLine(bestCost, iteration)

        avg_evalTimePerCandidate = 0.0
        if (total_evaluatedCandidates != 0):
            avg_evalTimePerCandidate = 1000.0 * total_elapsedEvalTime / float(total_evaluatedCandidates)

        print
        ''
        print
        'GRASP Candidate Evaluation Performance:'
        print
        '  Num. Candidates Eval.', total_evaluatedCandidates
        print
        '  Total Eval. Time     ', total_elapsedEvalTime, 's'
        print
        '  Avg. Time / Candidate', avg_evalTimePerCandidate, 'ms'

        localSearch.printPerformance()

        return (bestSolution)
