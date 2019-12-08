from collections import deque

from Aircraft import Aircraft


# structure used to represent a departure queue
class TakeOffQueue(deque):
    def __init__(self):
        deque.__init__(self)

        self.currentTime = 0
        self.nextAvailable = 0
        self.lastPlane = Aircraft('nil', 0, 0, 0, 0)
        self.totalFuelBurned = 0
        self.totalDelayCost = 0

    def print(self):
        print("next available " + str(self.nextAvailable))
        for plane in self:
            plane.printAircraft()
        print("\n")

    # depart aircraft if available, otherwise update time
    def update(self, newTime):
        self.currentTime = newTime
        self.nextAvailable = max(self.nextAvailable, self.currentTime)
        if len(self) > 0 and self.nextAvailable <= self.currentTime:
            self.lastPlane = self.popleft()
            res = self.lastPlane.depart(self.nextAvailable, self)
            self.nextAvailable = self.nextAvailable + self.lastPlane.delayToOthers
            return res + self.update(newTime)
        return 0, 0

    # insert new plane into queue at appropriate index
    def insertIntoTakeoffQueue(self, plane):
        res = self.update(plane.arrivalTime)
        self.insert(plane.findIndex(self), plane)
        return res


# takeoff queue without re-ordering
class DefaultTakeOffQueue(TakeOffQueue):
    def insertIntoTakeoffQueue(self, plane):
        self.append(plane)
        return self.update(plane.arrivalTime)

