class Bus(object):
    def __init__(self, busId, cap, eurosMin, eurosKm):
        self._busId = busId
        self._capacity = cap
        self._eurosMin = eurosMin
        self._eurosKm = eurosKm

    def getId(self):
        return self._busId

    def getCapacity(self):
        return self._capacity

    def getEurosMin(self):
        return self._eurosMin

    def getEurosKm(self):
        return self._eurosKm

