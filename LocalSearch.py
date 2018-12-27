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

    def createNeighborSolutionBus(self, solution, oldAssignment, newAssignment):

        newSolution = copy.deepcopy(solution)
        
        newSolution.unassignBus(oldAssignment)

        feasible = newSolution.assignBus(newAssignment)
        if(not feasible): return(None)
        
        return(newSolution)

    def createNeighborSolutionDriver(self, solution, oldAssignment, newAssignment):

        newSolution = copy.deepcopy(solution)

        newSolution.unassignDriver(oldAssignment)

        feasible = newSolution.assignDriver(newAssignment)
        if (not feasible): return (None)

        return (newSolution)

    def createNeighborSolutionDriver(self, solution, assignment, newDriver):

        newSolution = copy.deepcopy(solution)

        newSolution.unassignDriver(assignment, newDriver)

        assignment.bus = newDriver
        feasible = newSolution.assignDriver(assignment)
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
    
    def exploreNeighborhoodBus(self, solution, sortedBusAssignments):
        curHighestCost = solution.cost
        for assignment in sortedBusAssignments:
            curServices, posBuses = solution.findBusesInOtherServices(assignment.bus)
            for posBus in posBuses[assignment.service]:
                newAssignment, neighborHighestCost = solution.evaluateChangeBus(assignment, posBus)
                if (curHighestCost > neighborHighestCost):
                    neighbor = self.createNeighborSolutionBus(solution, assignment, newAssignment)
                    if (neighbor is None): continue
                    if (self.policy == 'FirstImprovement'):
                        return (neighbor)
                    else:
                        bestNeighbor = neighbor
                        curHighestCost = neighborHighestCost
        return bestNeighbor

    def exploreNeighborhoodDriver(self, solution, sortedDriverAssignments):
        curHighestCost = solution.cost
        for assignment in sortedDriverAssignments:
            curServices, posDrivers = solution.findDriversInOtherServices(assignment.driver)
            for posDriver in posDrivers[assignment.service]:
                newAssignment, neighborHighestCost = solution.evaluateChangeDriver(assignment, posDriver)
                if (curHighestCost > neighborHighestCost):
                    neighbor = self.createNeighborSolution(solution, assignment, posDriver)
                    if (neighbor is None): continue
                    if (self.policy == 'FirstImprovement'):
                        return (neighbor)
                    else:
                        bestNeighbor = neighbor
                        curHighestCost = neighborHighestCost
        return bestNeighbor

    def exploreNeighborhood(self, solution):
        bestNeighbor = solution
        
        if(self.nhStrategy == 'Reassignment'):
            sortedBusAssignments, sortedDriverAssignments = self.getDriversAndBusesAssignements(solution)

            neighborBus = self.exploreNeighborhoodBus(solution, sortedBusAssignments)
            neighbor = self.exploreNeighborhoodDriver(neighborBus, sortedDriverAssignments)

            return neighbor;
                            
        elif(self.nhStrategy == 'Exchange'):
            # For the Exchange neighborhood and first improvement policy, try exchanging
            # tasks two tasks, one from highly loaded CPU and the other from lowly loaded
            # CPU. It can be done by picking task1 from begin to end of sortedAssignments,
            # and task2 from end to begin.
            
            sortedAssignments = self.getAssignmentsSortedByCPULoad(solution)
            numAssignments = len(sortedAssignments)
            
            for i in xrange(0, numAssignments):             # i = 0..(numAssignments-1)
                assignment1 = sortedAssignments[i]
                
                task1 = assignment1[0]
                taskId1 = task1.getId()
                
                curCPU1 = assignment1[1]
                curCPUId1 = curCPU1.getId()
                
                for j in xrange(numAssignments-1, -1, -1):  # j = (numAssignments-1)..0
                    if(i >= j): continue # avoid duplicate explorations and exchange with itself. 
                    
                    assignment2 = sortedAssignments[j]
                    
                    task2 = assignment2[0]
                    taskId2 = task2.getId()
                    
                    curCPU2 = assignment2[1]
                    curCPUId2 = curCPU2.getId()

                    # avoid exploring pairs of tasks assigned to the same CPU
                    if(curCPUId1 == curCPUId2): continue
                    
                    changes = []
                    changes.append(Change(taskId1, curCPUId1, curCPUId2))
                    changes.append(Change(taskId2, curCPUId2, curCPUId1))
                    neighborHighestLoad = self.evaluateNeighbor(solution, changes)
                    if(curHighestLoad > neighborHighestLoad):
                        neighbor = self.createNeighborSolution(solution, changes)
                        if(neighbor is None): continue
                        if(self.policy == 'FirstImprovement'):
                            return(neighbor)
                        else:
                            bestNeighbor = neighbor
                            curHighestLoad = neighborHighestLoad
            
        else:
            raise Exception('Unsupported NeighborhoodStrategy(%s)' % self.nhStrategy)
        
        return(bestNeighbor)
    
    def run(self, solution):
        if(not self.enabled): return(solution)
        if(not solution.isFeasible()): return(solution)

        bestSolution = solution
        bestHighestLoad = bestSolution.cost
        
        startEvalTime = time.time()
        iterations = 0
        
        # keep iterating while improvements are found
        keepIterating = True
        while(keepIterating):
            keepIterating = False
            iterations += 1
            
            neighbor = self.exploreNeighborhood(bestSolution)
            curHighestLoad = neighbor.getHighestLoad()
            if(bestHighestLoad > curHighestLoad):
                bestSolution = neighbor
                bestHighestLoad = curHighestLoad
                keepIterating = True
        
        self.iterations += iterations
        self.elapsedTime += time.time() - startEvalTime
        
        return(bestSolution)
    
    def printPerformance(self):
        if(not self.enabled): return
        
        avg_evalTimePerIteration = 0.0
        if(self.iterations != 0):
            avg_evalTimePerIteration = 1000.0 * self.elapsedTime / float(self.iterations)
        #
        # print ''
        # print 'Local Search Performance:'
        # print '  Num. Iterations Eval.', self.iterations
        # print '  Total Eval. Time     ', self.elapsedTime, 's'
        # print '  Avg. Time / Iteration', avg_evalTimePerIteration, 'ms'
