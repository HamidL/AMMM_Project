import copy, time

# A change in a solution in the form: move taskId from curCPUId to newCPUId.
# This class is used to carry sets of modifications.
# A new solution can be created based on an existing solution and a list of
# changes can be created using the createNeighborSolution(solution, changes) function.
class Change(object):
    def __init__(self, taskId, curCPUId, newCPUId):
        self.taskId = taskId
        self.curCPUId = curCPUId
        self.newCPUId = newCPUId

# Implementation of a local search using two neighborhoods and two different policies.
class LocalSearch(object):
    def __init__(self, config):
        self.enabled = config.localSearch
        self.nhStrategy = config.neighborhoodStrategy
        self.policy = config.policy
        
        self.elapsedTime = 0
        self.iterations = 0

    def createNeighborSolution(self, solution, changes):
        # unassign the tasks specified in changes
        # and reassign them to the new CPUs
        
        newSolution = copy.deepcopy(solution)
        
        for change in changes:
            newSolution.unassign(change.taskId, change.curCPUId)
        
        for change in changes:
            feasible = newSolution.assign(change.taskId, change.newCPUId)
            if(not feasible): return(None)
        
        return(newSolution)
    
    
    def evaluateNeighbor(self, solution, changes):
        newAvailCapPerCPUId = copy.deepcopy(solution.availCapacityPerCPUId)
        newAvailCapPerCoreId = copy.deepcopy(solution.availCapacityPerCoreId)

        for change in changes:
            taskId = change.taskId
            task = solution.tasks[taskId]
            taskThreadIds = task.getThreadIds()
            
            curCPUId = change.curCPUId
            
            for threadId in taskThreadIds:
                resources = task.getResourcesByThread(threadId)
                coreId = solution.getCoreIdAssignedToThreadId(threadId)
                newAvailCapPerCoreId[coreId] += resources
                newAvailCapPerCPUId[curCPUId] += resources

        for change in changes:
            taskId = change.taskId
            task = solution.tasks[taskId]
            taskThreadIds = task.getThreadIds()
            
            newCPUId = change.newCPUId
            cpu = solution.cpus[newCPUId]
            cpuCoreIds = cpu.getCoreIds()
            
            for threadId in taskThreadIds:
                resources = task.getResourcesByThread(threadId)
                selectedCoreId = None
                selectedCoreAvailCap = 0
                for coreId in cpuCoreIds:
                    coreAvailCap = newAvailCapPerCoreId[coreId]
                    if((coreAvailCap >= resources) and (coreAvailCap > selectedCoreAvailCap)):
                        selectedCoreId = coreId
                        selectedCoreAvailCap = coreAvailCap
                
                if(selectedCoreId is None):
                    return(float('infinity'))
                
                newAvailCapPerCoreId[selectedCoreId] -= resources
                newAvailCapPerCPUId[newCPUId] -= resources

        highestLoad = 0.0
        for cpu in solution.cpus:
            cpuId = cpu.getId()
            totalCapacity = cpu.getTotalCapacity()
            availableCapacity = newAvailCapPerCPUId[cpuId]
            highestLoad = max(highestLoad, (totalCapacity - availableCapacity) / totalCapacity)
            
        return(highestLoad)
    
    def getAssignmentsSortedByCost(self, solution):
        buses = solution.getBuses()
        drivers = solution.getDrivers()
        services = solution.getServices()
        
        # create vector of task assignments.
        # Each element is a tuple <task, cpu> 
        busAssignments = []
        busCosts = solution.getBusCosts()
        for b in buses:
            busId = b.getId()
            serviceId = solution.getServiceIdAssignedToBusId(busId)
            service = services[serviceId]
            cost = solution.busCostPerServiceId(serviceId)
            assignment = (b, service, cost)
            busAssignments.append(assignment)

        driverAssignments = []
        driverCost = solution.getDriverCosts()
        for d in drivers:
            driverId = d.getId()
            serviceId = solution.getServiceIdAssignedToBusId(busId)
            service = services[serviceId]
            cost = driverCost[d]
            assignment = (d, service, cost)
            driverAssignments.append(assignment)

        # For best improvement policy it does not make sense to sort the tasks since all of them must be explored.
        # However, for first improvement, we can start by the tasks assigned to the more loaded CPUs.
        if(self.policy == 'BestImprovement'): return(busAssignments,driverAssignments)
        
        # Sort task assignments by the cost of the assigned Service in descending order.
        sortedBusAssignments = sorted(busAssignments, key=lambda busAssignment:busAssignment[2], reverse=True)
        sortedDriverAssignments = sorted(driverAssignments, key=lambda driverAssignment:driverAssignment[2], reverse=True)
        return(sortedBusAssignments,sortedDriverAssignments)
    
    def exploreNeighborhood(self, solution):
        services = solution.getServices()
        
        curCost = solution.cost
        bestNeighbor = solution
        
        if(self.nhStrategy == 'Reassignment'):
            sortedAssignments = self.getAssignmentsSortedByCost(solution)
                
            for assignment in sortedAssignments:
                task = assignment[0]
                taskId = task.getId()
                
                curCPU = assignment[1]
                curCPUId = curCPU.getId()
                
                for cpu in cpus:
                    newCPUId = cpu.getId()
                    if(newCPUId == curCPUId): continue
                    
                    changes = []
                    changes.append(Change(taskId, curCPUId, newCPUId))
                    neighborHighestLoad = self.evaluateNeighbor(solution, changes)
                    if(curHighestLoad > neighborHighestLoad):
                        neighbor = self.createNeighborSolution(solution, changes)
                        if(neighbor is None): continue
                        if(self.policy == 'FirstImprovement'):
                            return(neighbor)
                        else:
                            bestNeighbor = neighbor
                            curHighestLoad = neighborHighestLoad
                            
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
