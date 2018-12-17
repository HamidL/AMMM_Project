from Driver import Driver

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

        self.OV = [[0]*nServices]*nServices

        for s1 in range(0, nServices):
            for s2 in range(s1+1, nServices):
                if (ST[s1] <= ST[s2] and ST[s2] <= ST[s1]+DM[s1]) or (ST[s2] <= ST[s1] and ST[s1] <= ST[s2]+DM[s2]):
                    self.OV[s1][s2] = 1
                    self.OV[s2][s1] = 1

        self.drivers = []
        for d in range(0, nDrivers):
            self.drivers.append(Driver(d, maxD[d]))

    def getDrivers(self):
        return self.drivers