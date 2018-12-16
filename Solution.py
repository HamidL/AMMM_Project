import copy
import time
from Problem import Problem


# Assignment class stores the assignment of a driver and a bus to a certain service
class Assignment(object):
    def __init__(self, driver, bus, service):
        self.driver = driver
        self.bus = bus
        self.service = service


# Solution includes functions to manage the solution, to perform feasibility
# checks and to dump the solution into a string or file.
class Solution(Problem):
    @staticmethod
    def createEmptySolution(config, problem):
        solution = Solution(problem.inputData)
        solution.setVerbose(config.verbose)
        return solution

    def __init__(self, inputData):
        super(Solution, self).__init__(inputData)

        self.driver_to_services = []  # array: driver => services
        for i in range(0, self.nDrivers):
            self.driver_to_services.append([])

        self.service_to_drivers = []  # array: service => drivers
        for i in range(0, self.nServices):
            self.service_to_drivers.append([])

        self.bus_to_services = []  # hash table: bus => services
        for i in range(0, self.nBuses):
            self.bus_to_services.append([])

        self.service_to_buses = []  # hash table: service => buses
        for i in range(0, self.nServices):
            self.service_to_buses.append([])

        self.worked_minutes = [0] * self.nDrivers  # array of worked minutes for each driver
        self.used_buses = 0

        self.feasible = True

    def makeInfeasible(self):
        self.feasible = False

    def isFeasible(self):
        return (self.feasible)

    def isFeasibleToAssignDriverToService(self, driverId, serviceId):
        if self.worked_minutes[driverId] + self.DM[serviceId] > self.maxD[driverId]:
            return False
        for service in self.driver_to_services[driverId]:
            if self.OV[service][serviceId]:
                return False
        return True

    def isFeasibleToAssignBusToService(self, busId, serviceId):
        for service in self.bus_to_services[busId]:
            if self.OV[service][serviceId]:
                return False
        if len(self.bus_to_services[busId]) == 0 and self.used_buses == self.maxBuses:
            return False
        return True

    def getBusesAssignedToService(self, serviceId):
        if len(self.service_to_buses[serviceId]) == 0:
            return None
        return self.service_to_buses[serviceId]

    def getDriversAssignedToService(self, serviceId):
        if len(self.service_to_drivers[serviceId]) == 0:
            return None
        return self.service_to_drivers[serviceId]

    def assign(self, driverId, busId, serviceId):
        if not self.isFeasibleToAssignDriverToService(driverId, serviceId):
            return False
        if not self.isFeasibleToAssignBusToService(busId, serviceId):
            return False

        if len(self.bus_to_services[busId]) == 0:  # if it was not being used, add 1 to used_buses
            self.used_buses += 1

        self.bus_to_services[busId].append(serviceId)  # add service to list of bus services
        self.service_to_buses[serviceId].append(busId)  # add bus to list of service buses

        self.worked_minutes[driverId] += self.DM[serviceId]  # add minutes worked to driver
        self.driver_to_services[driverId].append(serviceId)  # add service to list of driver services
        self.service_to_drivers[serviceId].append(driverId)  # add driver to list of service drivers

        return True

    def unassign(self, driverId, busId, serviceId):
        # is it really necessary to check if is possible to unasign??
        self.worked_minutes[driverId] -= self.DM[serviceId]
        self.driver_to_services[driverId].remove(serviceId)

        self.service_to_drivers[serviceId].remove(driverId)

        self.bus_to_services[busId].remove(serviceId)
        if(len(self.bus_to_services[busId]) == 0):
            self.used_buses -= 1

        self.service_to_buses[serviceId].remove(busId)

        return True

    def getHighestLoad(self):
        return (self.highestLoad)

    def findFeasibleAssignments(self, taskId):
        startEvalTime = time.time()
        evaluatedCandidates = 0

        feasibleAssignments = []
        for cpu in self.cpus:
            cpuId = cpu.getId()
            feasible = self.assign(taskId, cpuId)

            evaluatedCandidates += 1
            if (not feasible): continue

            assignment = Assignment(taskId, cpuId, self.getHighestLoad())
            feasibleAssignments.append(assignment)

            self.unassign(taskId, cpuId)

        elapsedEvalTime = time.time() - startEvalTime
        return (feasibleAssignments, elapsedEvalTime, evaluatedCandidates)

    def findBestFeasibleAssignment(self, taskId):
        bestAssignment = Assignment(taskId, None, float('infinity'))
        for cpu in self.cpus:
            cpuId = cpu.getId()
            feasible = self.assign(taskId, cpuId)
            if (not feasible): continue

            curHighestLoad = self.getHighestLoad()
            if (bestAssignment.highestLoad > curHighestLoad):
                bestAssignment.cpuId = cpuId
                bestAssignment.highestLoad = curHighestLoad

            self.unassign(taskId, cpuId)

        return (bestAssignment)

    def __str__(self):  # toString equivalent
        nTasks = self.inputData.nTasks
        nThreads = self.inputData.nThreads
        nCPUs = self.inputData.nCPUs
        nCores = self.inputData.nCores

        strSolution = 'z = %10.8f;\n' % self.highestLoad

        # Xhk: decision variable containing the assignment of threads to cores
        # pre-fill with no assignments (all-zeros)
        xhk = []
        for h in xrange(0, nThreads):  # h = 0..(nThreads-1)
            xhkEntry = [0] * nCores  # results in a vector of 0's with nCores elements
            xhk.append(xhkEntry)

        # iterate over hash table threadIdToCoreId and fill in xhk
        for threadId, coreId in self.threadIdToCoreId.iteritems():
            xhk[threadId][coreId] = 1

        strSolution += 'xhk = [\n'
        for xhkEntry in xhk:
            strSolution += '\t[ '
            for xhkValue in xhkEntry:
                strSolution += str(xhkValue) + ' '
            strSolution += ']\n'
        strSolution += '];\n'

        # Xtc: decision variable containing the assignment of tasks to CPUs
        # pre-fill with no assignments (all-zeros)
        xtc = []
        for t in xrange(0, nTasks):  # t = 0..(nTasks-1)
            xtcEntry = [0] * nCPUs  # results in a vector of 0's with nCPUs elements
            xtc.append(xtcEntry)

        # iterate over hash table taskIdToCPUId and fill in xtc
        for taskId, cpuId in self.taskIdToCPUId.iteritems():
            xtc[taskId][cpuId] = 1

        strSolution += 'xtc = [\n'
        for xtcEntry in xtc:
            strSolution += '\t[ '
            for xtcValue in xtcEntry:
                strSolution += str(xtcValue) + ' '
            strSolution += ']\n'
        strSolution += '];\n'

        return (strSolution)

    def saveToFile(self, filePath):
        f = open(filePath, 'w')
        f.write(self.__str__())
        f.close()
