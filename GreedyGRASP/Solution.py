import numpy as np
from GreedyGRASP.Problem import Problem
from copy import deepcopy


# Assignment class stores the assignment of a driver and a bus to a certain service
class BusAssignment(object):
    def __init__(self, busId, serviceId, cost):
        self.bus = busId
        self.service = serviceId
        self.cost = cost
        self._greedyCost = 0

    @property
    def greedyCost(self):
        return self._greedyCost

    @greedyCost.setter
    def greedyCost(self, cost):
        self._greedyCost = cost

    def equal(self, busAssignment):
        if busAssignment.bus == self.bus and busAssignment.service == self.service:
            return True
        return False

class DriverAssignment(object):
    def __init__(self, driverId, serviceId, cost):
        self.driver = driverId
        self.service = serviceId
        self.cost = cost

    def equal(self, driverAssignment):
        if driverAssignment.driver == self.driver and driverAssignment.service == self.service:
            return True
        return False


# Solution includes functions to manage the solution, to perform feasibility
# checks and to dump the solution into a string or file.
class Solution(Problem):
    @staticmethod
    def createEmptySolution(config, problem):
        solution = Solution(problem.inputData)
        # solution.setVerbose(config.verbose)
        return solution

    def __init__(self, inputData):
        super(Solution, self).__init__(inputData)

        self.driver_to_services = []  # array: driver => services
        for i in range(0, self.inputData.nDrivers):
            self.driver_to_services.append([])

        self.service_to_drivers = []  # array: service => drivers
        for i in range(0, self.inputData.nServices):
            self.service_to_drivers.append([])

        self.bus_to_services = []  # hash table: bus => services
        for i in range(0, self.inputData.nBuses):
            self.bus_to_services.append([])

        self.service_to_buses = []  # hash table: service => buses
        for i in range(0, self.inputData.nServices):
            self.service_to_buses.append([])

        self.busAssignments = []

        self.driverAssignments = []

        self.worked_minutes = [0] * self.inputData.nDrivers  # array of worked minutes for each driver
        self.used_buses = 0
        self.cost = 0

        self.feasible = True

    def makeInfeasible(self):
        self.feasible = False
        self.cost = float('infinity')

    def isFeasible(self):
        return (self.feasible)

    def isFeasibleToAssignDriverToService(self, driverId, serviceId):
        if self.worked_minutes[driverId] + self.getServices()[serviceId].getMinutes() > self.getDrivers()[driverId].getMaxD():
            return False
        for service in self.driver_to_services[driverId]:
            if self.OV[service][serviceId]:
                return False
        return True

    def isFeasibleToAssignBusToService(self, busId, serviceId):
        for service in self.bus_to_services[busId]:
            if self.OV[service][serviceId]:
                return False
        if len(self.bus_to_services[busId]) == 0 and self.used_buses == self.inputData.maxBuses:
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

    def getServicesAssignedToBus(self, busId):
        if len(self.bus_to_services[busId]) == 0:
            return None
        return self.bus_to_services[busId]

    def getServicesAssignedToDriver(self, driverId):
        if len(self.driver_to_services[driverId]) == 0:
            return None
        return self.driver_to_services[driverId]

    def getBusAssignments(self):
        return self.busAssignments

    def getBusAssignments(self, busId):
        busAssignments = []
        for ass in self.busAssignments:
            if ass.bus == busId:
                busAssignments.append(ass)
        return busAssignments

    def getDriverAssignments(self):
        return self.driverAssignments

    def getDriverAssignments(self, driverId):
        driverAssignments = []
        for ass in self.driverAssignments:
            if ass.driver == driverId:
                driverAssignments.append(ass)
        return driverAssignments

    def getDriverCosts(self):
        costs = [0] * self.inputData.nDrivers
        for i in range(0, self.inputData.nDrivers):
            costs[i] = self._costsDriver(self.worked_minutes[i])
        return costs

    def getBusCosts(self):
        costs = [0] * self.inputData.nBuses
        for i in range(0, self.inputData.nBuses):
            minutesBus = 0
            kmsBus = 0
            for service in self.bus_to_services[i]:
                minutesBus += self.inputData.DM[service]
                kmsBus += self.inputData.DK[service]
            costs[i] += minutesBus * self.getBuses()[i].getEurosMin() + kmsBus * self.getBuses()[i].getEurosKm()
        return costs

    def _costsDriver(self, workedMinutes):
        cost = 0
        if self.inputData.BM - workedMinutes > 0:
            cost = self.inputData.CBM * workedMinutes
        else:  # all cost is extra
            cost = self.inputData.BM * self.inputData.CBM + \
                   (workedMinutes - self.inputData.BM) * self.inputData.CEM
        return cost

    def assign(self, driverAssignment, busAssignment):
        if not self.isFeasibleToAssignDriverToService(driverAssignment.driver, driverAssignment.service):
            return False
        if not self.isFeasibleToAssignBusToService(busAssignment.bus, busAssignment.service):
            return False

        if len(self.bus_to_services[busAssignment.bus]) == 0:  # if it was not being used, add 1 to used_buses
            self.used_buses += 1

        self.bus_to_services[busAssignment.bus].append(busAssignment.service)  # add service to list of bus services
        self.service_to_buses[busAssignment.service].append(busAssignment.bus)  # add bus to list of service buses
        self.cost += driverAssignment.cost + busAssignment.cost
        self.busAssignments.append(busAssignment)

        self.worked_minutes[driverAssignment.driver] += self.getServices()[driverAssignment.service].getMinutes()  # add minutes worked to driver
        self.driver_to_services[driverAssignment.driver].append(driverAssignment.service)  # add service to list of driver services
        self.service_to_drivers[driverAssignment.service].append(driverAssignment.driver)  # add driver to list of service drivers
        self.driverAssignments.append(driverAssignment)

        return True

    def assignBus(self, busAssignment):
        if not self.isFeasibleToAssignBusToService(busAssignment.bus, busAssignment.service):
            return False

        if len(self.bus_to_services[busAssignment.bus]) == 0:
            self.used_buses += 1
        self.bus_to_services[busAssignment.bus].append(busAssignment.service)
        self.service_to_buses[busAssignment.service].append(busAssignment.bus)  # add bus to list of service buses
        self.cost += busAssignment.cost
        self.busAssignments.append(busAssignment)

        return True

    def assignDriver(self, driverAssignment):
        if not self.isFeasibleToAssignDriverToService(driverAssignment.driver, driverAssignment.service):
            return False

        self.worked_minutes[driverAssignment.driver] += self.getServices()[driverAssignment.service].getMinutes()  # add minutes worked to driver
        self.driver_to_services[driverAssignment.driver].append(driverAssignment.service)  # add service to list of driver services
        self.service_to_drivers[driverAssignment.service].append(driverAssignment.driver)  # add driver to list of service drivers
        self.driverAssignments.append(driverAssignment)

        return True

    def unassign(self, driverAssignment, busAssignment):
        # is it really necessary to check if is possible to unasign??
        self.worked_minutes[driverAssignment.driver] -= self.inputData.getServices()[driverAssignment.service].getMinutes()
        self.driver_to_services[driverAssignment.driver].remove(driverAssignment.service)
        self.service_to_drivers[driverAssignment.service].remove(driverAssignment.driver)
        for ass in self.driverAssignments:
            if ass.equal(driverAssignment):
                self.driverAssignments.remove(ass)
                break

        if len(self.bus_to_services[busAssignment.bus]) == 1:
            self.used_buses -= 1
        self.bus_to_services[busAssignment.bus].remove(busAssignment.service)
        self.service_to_buses[busAssignment.service].remove(busAssignment.bus)
        for ass in self.busAssignments:
            if ass.equal(busAssignment):
                self.busAssignments.remove(ass)
                break

        return True

    def unassignDriver(self, driverAssignment):
        self.worked_minutes[driverAssignment.driver] -= self.getServices()[driverAssignment.service].getMinutes()
        self.driver_to_services[driverAssignment.driver].remove(driverAssignment.service)
        self.service_to_drivers[driverAssignment.service].remove(driverAssignment.driver)
        for ass in self.driverAssignments:
            if ass.equal(driverAssignment):
                self.driverAssignments.remove(ass)
                break

        return True

    def unassignBus(self, busAssignment):
        if len(self.bus_to_services[busAssignment.bus]) == 1:
            self.used_buses -= 1
        self.bus_to_services[busAssignment.bus].remove(busAssignment.service)
        self.service_to_buses[busAssignment.service].remove(busAssignment.bus)
        for ass in self.busAssignments:
            if ass.equal(busAssignment):
                self.busAssignments.remove(ass)
                break

        return True

    def findFeasibleAssignments(self, serviceId):
        busesAssignments = []
        driversAssignments = []
        for i in range(0, self.inputData.nBuses):
            if self.isFeasibleToAssignBusToService(i, serviceId):
                cost = self.getServices()[serviceId].getMinutes() * self.getBuses()[i].getEurosMin() + self.getServices()[serviceId].getKm() * self.getBuses()[i].getEurosKm()
                busesAssignments.append(BusAssignment(i, serviceId, cost))
        for i in range(0, self.inputData.nDrivers):
            if self.isFeasibleToAssignDriverToService(i, serviceId):
                cost = 0
                if self.inputData.BM - self.worked_minutes[i] > 0:
                    if (self.inputData.BM - (self.worked_minutes[i] + self.getServices()[serviceId].getMinutes())) >= 0:  # all cost is "normal"
                        cost = self.getServices()[serviceId].getMinutes() * self.inputData.CBM
                    else:  # some cost is "normal" and some is extra
                        cost = (self.inputData.BM - self.worked_minutes[i]) * self.inputData.CBM + \
                               (self.getServices()[serviceId].getMinutes() - (self.inputData.BM - self.worked_minutes[i])) * self.inputData.CEM
                else:  # all cost is extra
                    cost = self.getServices()[serviceId].getMinutes() * self.inputData.CEM
                driversAssignments.append(DriverAssignment(i, serviceId, cost))

        return busesAssignments, driversAssignments

    def findBestFeasibleAssignment(self, serviceId):
        # drivers: el que haya trabajado menos hasta llegar a BM, en el caso de que sea igual, el que tenga menos tiempo
        # trabajado en general
        notExtratimeWorkers = np.zeros((self.inputData.nDrivers), dtype=int)
        for i in range(0, self.inputData.nDrivers):
            if self.worked_minutes[i] + self.getServices()[serviceId].getMinutes() < self.inputData.BM[i] and \
                    self.isFeasibleToAssignDriverToService(i, serviceId):
                notExtratimeWorkers[i] = 1
        driverAssignment = None
        if driverAssignment is None:  # all of them would enter extra hours period, select the minimum directly
            for i in range(0, self.inputData.nDrivers):
                pass
        busAssignment = None

    def _overlapping(self, servicesA, servicesB):
        for service in servicesA:
            for nested_service in servicesB:
                if self.OV[service][nested_service]:
                    return True
        return False

    def findBusesInOtherServices(self, busId):
        buses = []
        services = deepcopy(self.bus_to_services[busId])
        total_buses = [x for x in range(0, self.inputData.nBuses)]
        index = 0
        for service in services:
            buses.append([])
            diff_buses = [x for x in total_buses if x not in self.service_to_buses[service]]
            for bus in diff_buses:
                if not self._overlapping(services, self.bus_to_services[bus]):
                    buses[index].append(bus)
            index += 1
        return services, buses

    def findDriversInOtherServices(self, driverId):
        drivers = []
        services = deepcopy(self.driver_to_services[driverId])
        total_drivers = [x for x in range(0, self.inputData.nDrivers)]
        index = 0
        for service in services:
            drivers.append([])
            diff_drivers = [x for x in total_drivers if x not in self.service_to_drivers[service]]
            for driver in diff_drivers:
                if not self._overlapping(services, self.driver_to_services[driver]):
                    drivers[index].append(driver)
            index += 1
        return services, drivers

    def evaluateReassignment(self, assignment, id):
        if type(assignment) == BusAssignment:
            cost = self.cost
            cost -= assignment.cost
            busAssignment = None
            if self.isFeasibleToAssignBusToService(id, assignment.service):
                newcost = self.getServices()[assignment.service].getMinutes() * self.getBuses()[id].getEurosMin() +\
                        self.getServices()[assignment.service].getKm() * self.getBuses()[id].getEurosKm()
                busAssignment = BusAssignment(assignment.bus, assignment.service, newcost)
                cost += newcost
            else:
                return None, float('infinity')
            return busAssignment, cost
        elif type(assignment) == DriverAssignment:
            cost = self.cost
            cost -= assignment.cost
            driverAssignment = None
            if self.isFeasibleToAssignDriverToService(id, assignment.service):
                newcost = 0
                if self.inputData.BM - self.worked_minutes[id] > 0:
                    if (self.inputData.BM - (self.worked_minutes[id] + self.getServices()[assignment.service].getMinutes())) >= 0:  # all cost is "normal"
                        newcost = self.getServices()[assignment.service].getMinutes() * self.inputData.CBM
                    else:  # some cost is "normal" and some is extra
                        newcost = (self.inputData.BM - self.worked_minutes[id]) * self.inputData.CBM + \
                               (self.getServices()[assignment.service].getMinutes() - (self.inputData.BM - self.worked_minutes[id])) * self.inputData.CEM
                else:  # all cost is extra
                    newcost = self.getServices()[assignment.service].getMinutes() * self.inputData.CEM
                cost += newcost
                driverAssignment = DriverAssignment(id, assignment.service, newcost)
            else:
                return None, float('infinity')
            return driverAssignment, cost
        else:
            return None, float('infinity')

    def evaluateExchange(self, assignment1, assignment2):
        if type(assignment1) == BusAssignment:
            cost = self.cost
            cost -= assignment1.cost
            cost -= assignment2.cost
            busAssignment = []
            if self.isFeasibleToAssignBusToService(assignment1.bus, assignment2.service) and \
                    self.isFeasibleToAssignBusToService(assignment2.bus, assignment1.service):
                newcost = self.getServices()[assignment2.service].getMinutes() * self.getBuses()[assignment1.bus].getEurosMin() + \
                          self.getServices()[assignment2.service].getKm() * self.getBuses()[assignment1.bus].getEurosKm()
                busAssignment.append(BusAssignment(assignment1.bus, assignment2.service, newcost))
                cost += newcost
                newcost = self.getServices()[assignment1.service].getMinutes() * self.getBuses()[assignment2.bus].getEurosMin() + \
                          self.getServices()[assignment1.service].getKm() * self.getBuses()[assignment2.bus].getEurosKm()
                busAssignment.append(BusAssignment(assignment2.bus, assignment1.service, newcost))
                cost += newcost
            else:
                return None, float('infinity')
            return busAssignment, cost
        elif type(assignment1) == DriverAssignment:
            cost = self.cost
            cost -= assignment1.cost
            cost -= assignment2.cost
            driverAssignment = []
            if self.isFeasibleToAssignDriverToService(assignment1.driver, assignment2.service) and \
                    self.isFeasibleToAssignDriverToService(assignment2.driver, assignment1.service):
                newcost = 0
                if self.inputData.BM - self.worked_minutes[assignment1.driver] > 0:
                    if (self.inputData.BM - (self.worked_minutes[assignment1.driver] + self.getServices()[assignment2.service].getMinutes())) >= 0:  # all cost is "normal"
                        newcost = self.getServices()[assignment2.service].getMinutes() * self.inputData.CBM
                    else:  # some cost is "normal" and some is extra
                        newcost = (self.inputData.BM - self.worked_minutes[assignment1.driver]) * self.inputData.CBM + \
                               (self.getServices()[assignment2.service].getMinutes() - (self.inputData.BM - self.worked_minutes[assignment1.driver])) * self.inputData.CEM
                else:  # all cost is extra
                    newcost = self.getServices()[assignment2.service].getMinutes() * self.inputData.CEM
                cost += newcost
                driverAssignment.append(DriverAssignment(assignment1.driver, assignment2.service, newcost))
                newcost = 0
                if self.inputData.BM - self.worked_minutes[assignment2.driver] > 0:
                    if (self.inputData.BM - (self.worked_minutes[assignment2.driver] + self.getServices()[assignment1.service].getMinutes())) >= 0:  # all cost is "normal"
                        newcost = self.getServices()[assignment1.service].getMinutes() * self.inputData.CBM
                    else:  # some cost is "normal" and some is extra
                        newcost = (self.inputData.BM - self.worked_minutes[assignment2.driver]) * self.inputData.CBM + \
                               (self.getServices()[assignment1.service].getMinutes() - (self.inputData.BM - self.worked_minutes[assignment2.driver])) * self.inputData.CEM
                else:  # all cost is extra
                    newcost = self.getServices()[assignment1.service].getMinutes() * self.inputData.CEM
                cost += newcost
                driverAssignment.append(DriverAssignment(assignment2.driver, assignment1.service, newcost))
            else:
                return None, float('infinity')
            return driverAssignment, cost
        else:
            return None, float('infinity')

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
