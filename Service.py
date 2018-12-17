class Service(object):
    def __init__(self, serviceId, passengers, km, startingTime, minutes, overlapping):
        self._serviceId = serviceId
        self._passengers = passengers
        self._km = km
        self._startingTime = startingTime
        self._minutes = minutes
        self._overlapping = overlapping

    def getId(self):
        return self._serviceId

    def getPassengers(self):
        return self._passengers

    def getKm(self):
        return self._km

    def getStartingTime(self):
        return self._startingTime

    def getMinutes(self):
        return self._minutes

    def getOverlapping(self):
        return self._overlapping

    def getNumOverlappingServices(self):
        return sum(self._overlapping)