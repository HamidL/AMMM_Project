class Problem(object):
    def __init__(self, inputData):
        self.inputData = inputData

        nServices = self.inputData.nServices
        nDrivers = self.inputData.nDrivers
        nBuses = self.inputData.nBuses
        maxBuses = self.inputData.maxBuses
        BM = self.inputData.BM
        ST = self.inputData.ST
        DM = self.inputData.DM
        DK = self.inputData.DK
        NP = self.inputData.NP
        cap = self.inputData.cap
        eurosMin = self.inputData.eurosMin
        eurosKm = self.inputData.eurosKm
        maxD = self.inputData.maxD

        self.OV = [[0 for x in range(nServices)] for y in range(nServices)]

        for s1 in range(0, nServices):
            for s2 in range(s1+1, nServices):
                if (ST[s1] <= ST[s2] and ST[s2] <= ST[s1]+DM[s1]) or (ST[s2] <= ST[s1] and ST[s1] <= ST[s2]+DM[s2]):
                    self.OV[s1][s2] = 1
                    self.OV[s2][s1] = 1

    def getTasks(self):
        return (self.tasks)

    def getCPUs(self):
        return (self.cpus)

    def checkInstance(self):
        totalCapacityCPUs = 0.0
        maxCoreCapacity = 0.0
        for cpu in self.cpus:
            capacity = cpu.getTotalCapacity()
            totalCapacityCPUs += capacity
            for coreId in cpu.getCoreIds():
                capacity = cpu.getTotalCapacityByCore(coreId)
                maxCoreCapacity = max(maxCoreCapacity, capacity)

        totalResourcesTasks = 0.0
        for task in self.tasks:
            resources = task.getTotalResources()
            totalResourcesTasks += resources

            threadIds = task.getThreadIds()
            for threadId in threadIds:
                threadRes = task.getResourcesByThread(threadId)
                if (threadRes > maxCoreCapacity): return (False)

            feasible = False
            for cpu in self.cpus:
                capacity = cpu.getTotalCapacity()
                feasible = (resources < capacity)
                if (feasible): break

            if (not feasible): return (False)

        if (totalCapacityCPUs < totalResourcesTasks): return (False)

        return (True)
