class Driver(object):
    def __init__(self, driverId, maxD):
        self._driverId = driverId
        self._maxD = maxD
        self._workedHours = 0

    def getId(self):
        return (self._driverId)

    def getMaxD(self):
        return (self._maxD)

    def getWorkedHours(self):
        return (self._workedHours)