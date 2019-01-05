class Driver(object):
    def __init__(self, driverId, maxD):
        self._driverId = driverId
        self._maxD = maxD

    def getId(self):
        return (self._driverId)

    def getMaxD(self):
        return (self._maxD)
