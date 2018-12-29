import copy, time

# A change in a solution in the form: move taskId from curCPUId to newCPUId.
# This class is used to carry sets of modifications.
# A new solution can be created based on an existing solution and a list of
# changes can be created using the createNeighborSolution(solution, changes) function.
class Change(object):
    def __init__(self, fromId, toId, service):
        self.fromId = fromId
        self.toId = toId
        self.service = service

# Implementation of a local search using two neighborhoods and two different policies.
class LocalSearch(object):
    def __init__(self, config):
        self.enabled = config.localSearch
        self.nhStrategy = config.neighborhoodStrategy
        self.policy = config.policy
        
        self.elapsedTime = 0
        self.iterations = 0

    def createNeighborSolutionBusR(self, solution, oldAssignment, newAssignment):

        newSolution = copy.deepcopy(solution)
        
        newSolution.unassignBus(oldAssignment)

        feasible = newSolution.assignBus(newAssignment)
        if(not feasible): return(None)
        
        return(newSolution)

    def createNeighborSolutionDriverR(self, solution, oldAssignment, newAssignment):

        newSolution = copy.deepcopy(solution)

        newSolution.unassignDriver(oldAssignment)

        feasible = newSolution.assignDriver(newAssignment)
        if (not feasible): return (None)

        return (newSolution)

    def createNeighborSolutionBusE(self, solution, oldAssignements, newAssignements):
        newSolution = copy.deepcopy(solution)

        for oldAssi in oldAssignements:
            newSolution.unassignBus(oldAssi)

        for newAssi in newAssignements:
            feasible = newSolution.assignBus(newAssi)
            if (not feasible): return (None)

        return (newSolution)

    def createNeighborSolutionDriverE(self, solution, oldAssignements, newAssignements):

        newSolution = copy.deepcopy(solution)

        for oldAssi in oldAssignements:
            newSolution.unassignDriver(oldAssi)

        for newAssi in newAssignements:
            feasible = newSolution.assignDriver(newAssi)
            if (not feasible): return (None)

        return (newSolution)
    
    def getDriversAndBusesAssignements(self, solution):
        buses = solution.getBuses()

        busAssignments = solution.busAssignments
        driverAssignments = solution.driverAssignments
        if(self.policy == 'BestImprovement'): return busAssignments,driverAssignments

        sortedBusAssignments = sorted(busAssignments, key=lambda busAssignment:buses[busAssignment.bus].getEurosMin * buses[busAssignment.bus].getEurosKm, reverse=True)
        sortedDriverAssignments = sorted(driverAssignments, key=lambda driverAssignment:solution.worked_minutes[driverAssignment.driver], reverse=True)

        return sortedBusAssignments,sortedDriverAssignments
    
    def exploreNeighborhoodBusR(self, solution, sortedBusAssignments):
        curHighestCost = solution.cost
        bestNeighbor = solution
        for assignment in sortedBusAssignments:
            curServices, posBuses = solution.findBusesInOtherServices(assignment.bus)
            for posBus in posBuses[curServices.index(assignment.service)]:

                newAssignment, neighborHighestCost = solution.evaluateReassignment(assignment, posBus)
                if (curHighestCost > neighborHighestCost):
                    neighbor = self.createNeighborSolutionBusR(solution, assignment, newAssignment)
                    if (neighbor is None): continue
                    if (self.policy == 'FirstImprovement'):
                        return (neighbor)
                    else:
                        bestNeighbor = neighbor
                        curHighestCost = neighborHighestCost
        return bestNeighbor

    def exploreNeighborhoodBusE(self, solution, sortedBusAssignments):
        curHighestCost = solution.cost
        bestNeighbor = solution
        for assignment in sortedBusAssignments:
            curServices, posBuses = solution.findBusesInOtherServices(assignment.bus)

            for posBus in posBuses[curServices.index(assignment.service)]:
                for posBusAssi in solution.getBusAssignments(posBus):
                    newAssignements, neighborHighestCost = solution.evaluateExchange(assignment, posBusAssi)
                    if (curHighestCost > neighborHighestCost):
                        oldAssignements = [assignment, posBusAssi]
                        neighbor = self.createNeighborSolutionBusE(solution,oldAssignements, newAssignements)
                        if (neighbor is None): continue
                        if (self.policy == 'FirstImprovement'):
                            return (neighbor)
                        else:
                            bestNeighbor = neighbor
                            curHighestCost = neighborHighestCost
        return bestNeighbor

    def exploreNeighborhoodDriverR(self, solution, sortedDriverAssignments):
        curHighestCost = solution.cost
        bestNeighbor = solution
        for assignment in sortedDriverAssignments:
            curServices, posDrivers = solution.findDriversInOtherServices(assignment.driver)
            for posDriver in posDrivers[curServices.index(assignment.service)]:
                newAssignment, neighborHighestCost = solution.evaluateReassignment(assignment, posDriver)
                if (curHighestCost > neighborHighestCost):
                    neighbor = self.createNeighborSolutionDriverR(solution, assignment, newAssignment)
                    if (neighbor is None): continue
                    if (self.policy == 'FirstImprovement'):
                        return (neighbor)
                    else:
                        bestNeighbor = neighbor
                        curHighestCost = neighborHighestCost
        return bestNeighbor

    def exploreNeighborhoodDriverE(self, solution, sortedBusAssignments):
        curHighestCost = solution.cost
        bestNeighbor = solution
        for assignment in sortedBusAssignments:
            curServices, posDrivers = solution.findDriversInOtherServices(assignment.driver)

            for posDriver in posDrivers[curServices.index(assignment.service)]:
                for posBusAssi in solution.getDriverAssignments(posDriver):
                    newAssignements, neighborHighestCost = solution.evaluateExchange(assignment, posBusAssi)
                    if (curHighestCost > neighborHighestCost):
                        oldAssignements = [assignment, posBusAssi]
                        neighbor = self.createNeighborSolutionDriverE(solution,oldAssignements, newAssignements)
                        if (neighbor is None): continue
                        if (self.policy == 'FirstImprovement'):
                            return (neighbor)
                        else:
                            bestNeighbor = neighbor
                            curHighestCost = neighborHighestCost
        return bestNeighbor

    def exploreNeighborhood(self, solution):
        sortedBusAssignments, sortedDriverAssignments = self.getDriversAndBusesAssignements(solution)
        if(self.nhStrategy == 'Reassignment'):
            neighborBus = self.exploreNeighborhoodBusR(solution, sortedBusAssignments)
            neighbor = self.exploreNeighborhoodDriverR(neighborBus, sortedDriverAssignments)

            return neighbor
                            
        elif(self.nhStrategy == 'Exchange'):
            neighborBus = self.exploreNeighborhoodBusE(solution, sortedBusAssignments)
            neighbor = self.exploreNeighborhoodDriverE(neighborBus, sortedDriverAssignments)
            return neighbor
            
        else:
            raise Exception('Unsupported NeighborhoodStrategy(%s)' % self.nhStrategy)
        
        return(bestNeighbor)
    
    def run(self, solution):
        if(not self.enabled): return(solution)
        if(not solution.isFeasible()): return(solution)

        bestSolution = solution
        bestHighestCost = bestSolution.cost
        
        startEvalTime = time.time()
        iterations = 0
        
        # keep iterating while improvements are found
        keepIterating = True
        while(keepIterating):
            keepIterating = False
            iterations += 1
            
            neighbor = self.exploreNeighborhood(bestSolution)
            curHighestCost = neighbor.cost
            if (bestHighestCost > curHighestCost):
                bestSolution = neighbor
                bestHighestCost = curHighestCost
                keepIterating = True
        
        self.iterations += iterations
        self.elapsedTime += time.time() - startEvalTime
        
        return(bestSolution)
    
    def printPerformance(self):
        if(not self.enabled): return
        
        avg_evalTimePerIteration = 0.0
        if(self.iterations != 0):
            avg_evalTimePerIteration = 1000.0 * self.elapsedTime / float(self.iterations)

        print ('')
        print ('Local Search Performance:')
        print ('  Num. Iterations Eval.', self.iterations)
        print ('  Total Eval. Time     ', self.elapsedTime, 's')
        print ('  Avg. Time / Iteration', avg_evalTimePerIteration, 'ms')
