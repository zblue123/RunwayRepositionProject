from enum import Enum


class AircraftType(Enum):
    TURBOPROP = 1
    NARROW = 2
    HEAVY = 3


class Aircraft:
    def __init__(self, name, acType, capacity, fuelBurn, delayToOthers):
        self.name = name
        self.acType = acType
        self.fuelBurn = fuelBurn
        self.capacity = capacity
        self.delayToOthers = delayToOthers
        self.departTime = 0
        self.arrivalTime = 0
        self.delay = 0

    # assign arrival time
    def assignTime(self, arrivalTime):
        self.arrivalTime = arrivalTime

    # have aircraft depart, return its time and fuel costs from waiting
    def depart(self, currentTime, takeOffQueue):
        self.departTime = currentTime
        self.delay = currentTime - self.arrivalTime
        # self.printWithDelay()
        takeOffQueue.totalDelayCost += self.capacity * timeCost(self.arrivalTime, currentTime, 0)
        takeOffQueue.totalFuelBurned += self.fuelBurn / 60.0 * self.delay
        return self.delay, self.fuelBurn * self.delay

    # find aircraft's cost to queue if place in front of it
    def costToQueue(self, queue):
        mySum = 0
        for plane in queue:
            mySum += self.costToOther(plane, self.delayIfProceeds(plane))
        return mySum

    # find delay based on separation requirements by aircraft class
    def delayIfProceeds(self, plane):
        return 3 if plane.acType.value - self.acType.value > 1 else 2

    # find cost to other aircraft if this airplane preceeds it
    def costToOther(self, plane, delayCaused):
        baseVars = [plane.arrivalTime, plane.capacity, plane.fuelBurn, timeCost(0, 0, delayCaused), fuelCostPerKg,
                    self.arrivalTime, self.capacity, self.fuelBurn]
        temp = []
        for var in baseVars:
            for var2 in baseVars:
                temp.append(var * var2)
        baseVars.extend(temp)
        sum = 0
        for i in range(len(baseVars)):
            sum += baseVars[i] * params[i]
        return sum  # plane.capacity*timeCost(plane.arrivalTime, self.arrivalTime, delayCaused) + plane.fuelBurn/60.0 * delayCaused * fuelCostPerKg

    # find cost of waiting a certain amount of time
    def calcWaitingCost(self, time):
        return self.capacity * timeCost(0, 0, time) + self.fuelBurn / 60.0 * time

    # find index to insert aircraft into a queue
    def findIndex(self, queue):
        self.skipped = 0
        if len(queue) == 0:
            self.depart(self.arrivalTime, queue)
        elif len(queue) == 1:
            return 1

        self.skipped = len(queue)
        waitingTime = 0
        tempQueue = deque()
        for plane in queue:
            tempQueue.append(plane)
            waitingTime += self.delayIfProceeds(plane)
            # plane.printAircraft()
            # print('waiting cost: ' + str(self.calcWaitingCost(waitingTime)))
            # print('cost to queue: ' + str(self.costToQueue(tempQueue)))
            if self.calcWaitingCost(waitingTime) > self.costToQueue(tempQueue):
                self.skipped = len(tempQueue)
                return len(tempQueue)
        return len(queue)

    def printAircraft(self):
        print(self.name + ' arrives at: ' + str(self.arrivalTime))  # + ' and has delay: ' + str(self.delay))

    def printWithDelay(self):
        print(self.name + ' arrives at: ' + str(self.arrivalTime) + ' with delay: ' + str(self.delay) +
              ' and skipped ' + str(self.skipped) + ' aircraft in the queue')
