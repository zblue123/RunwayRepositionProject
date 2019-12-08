# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 13:19:46 2017

@author: zblue
"""

from __future__ import division
import numpy as np
import random as rand
import operator

from Queues import TakeOffQueue, DefaultTakeOffQueue
from Utils import setup, output

aircraftList = []
fuelCostPerKg = 0
dnaSize = 72
populationSize = 10 
generations = 80
params = []
bestValues = [[0 for x in range(dnaSize + 1)] for r in range(generations)]


# class used to handle simulation
class Simulation:
    def __init__(self):
        self.takeOffQueue = TakeOffQueue()
        self.defaultTakeOffQueue = DefaultTakeOffQueue()
        self.cost = 0
        self.timeCostSaved = 0
        self.fuelSaved = 0
        self.totalCostSaved = 0

    def run(self):
        # acKeys = np.array(aircraft.keys)
        currTime = 0.0
        # generate poisson arrivals, update queue, update default queue
        for i in range(0, 40):
            a = weightedChoice(aircraftList)
            currTime += rand.expovariate(2.5)
            a.assignTime(currTime)
            self.takeOffQueue.insertIntoTakeoffQueue(a)
            self.defaultTakeOffQueue.insertIntoTakeoffQueue(a)

        # update until all aircraft have departed
        while len(self.takeOffQueue) > 0:
            self.takeOffQueue.update(currTime)
            currTime += 1
        # calculate cost savings
        self.cost = self.takeOffQueue.totalDelayCost + self.takeOffQueue.totalFuelBurned * fuelCostPerKg
        self.timeCostSaved = self.takeOffQueue.totalDelayCost - self.defaultTakeOffQueue.totalDelayCost
        self.fuelSaved = self.takeOffQueue.totalFuelBurned - self.defaultTakeOffQueue.totalFuelBurned
        self.totalCostSaved = self.fuelSaved * fuelCostPerKg + self.timeCostSaved

#        print('Total fuel burned:         ' + str(self.takeOffQueue.totalFuelBurned))
#        print('Total default fuel burned: ' + str(self.defaultTakeOffQueue.totalFuelBurned))
#        print('Total fuel saved:          ' + str(self.fuelSaved))
#        print('Total delay cost:          ' + str(self.takeOffQueue.totalDelayCost))
#        print('Total default delay cost:  ' + str(self.defaultTakeOffQueue.totalDelayCost))
#        print('Total delay cost saved:    ' + str(self.timeCostSaved))
#        print('Total cost saved:          ' + str(self.totalCostSaved))
#        print('Total time (hours):        ' + str(currTime/60.0))
        return (self.cost-self.totalCostSaved)/self.cost


def runSim(parameters):
    global params
    global fuelCostPerKg
    params = parameters
    fuelCostPerKg = 1.821*0.3261
    simulation = Simulation()
    return simulation.run()


# generate random parameter value
def randomGeneVal():
    lins = np.linspace(-10, 10, num=100)
    randVal = np.random.randint(1, 100)
    return lins[randVal]


# generate random individual 
def randomIndividual():
    params = []
    for i in range(dnaSize):
        params.append(randomGeneVal())
    return params


# generate random population
def randomPopulation():
    pop = []
    for _ in range(populationSize):
        pop.append(randomIndividual())
    return pop


# pick sample from set with weighted probabilities
def weightedChoice(samples):
    totalWeight = sum(int(s[1]) for s in samples)
    randVal = rand.uniform(0, totalWeight)
    for sample, weight in samples:
        if randVal < weight:
            return sample
        randVal -= weight 
    return samples[-1]


# mutate a gene with certain probability
def mutate(dna, mutationChance):
    newDna = []
    for g in range(dnaSize):
        if int(rand.random()*mutationChance == 1):
            newDna.append(randomGeneVal())
        else: 
            newDna.append(dna[g])
            
    return newDna


# breed two individuals
def crossover(dna1, dna2):
    pos = int(rand.random()*dnaSize)
    return dna1[:pos] + dna2[pos:], dna2[:pos] + dna1[pos:]


# determine fitness of individual by running simulation
def fitness(individual):
    return runSim(individual)


# produce new generation from old population
def evolve(population, mutationChance, gen):
    weightedPopulation = selection(population, gen)
    population = [weightedPopulation[i][0] for i in range(len(weightedPopulation))]
    for _ in range(8):
        parent1 = weightedChoice(weightedPopulation)
        parent2 = weightedChoice(weightedPopulation)
        child1, child2 = crossover(parent1,parent2)
        population.append(mutate(child1, mutationChance))
        population.append(mutate(child2, mutationChance))
    return population


# sort population and select best individual
def selection(population, gen):       
    weightedPopulation = []
    for individual in population:
        fitnessLevel = fitness(individual)
        individualFitness = (individual, fitnessLevel)
        weightedPopulation.append(individualFitness)
    
    weightedPopulation.sort(key=operator.itemgetter(1))
    global bestValues
    # print('Best individual: '+str(weightedPopulation[len(population)-1][0]) +
    # ' with fitness: '+str(weightedPopulation[len(population)-1][1]))
    for i in range(dnaSize):
        bestValues[gen][i] = weightedPopulation[len(weightedPopulation) - 1][0][i]
    bestValues[gen][dnaSize] = weightedPopulation[len(weightedPopulation) - 1][1]

    # print('Worst individual: '+str(weightedPopulation[0][0]) + ' with fitness: '+str(weightedPopulation[0][1])+ '\n')
    return eliminate(weightedPopulation)


# eliminate the worst 4 solutions    
def eliminate(weightedPopulation):
    for _ in range(4):
        ind = randomIndividual()
        weightedPopulation.append((ind, fitness(ind)))
    weightedPopulation.sort(key=operator.itemgetter(1))
    weightedPopulation = weightedPopulation[-20:]
    return weightedPopulation

        
if __name__ == "__main__":
    aircraftList = setup()
    population = randomPopulation() 
    for gen in range(generations):
        population = evolve(population, 0.1, gen)
    output(bestValues)
    print('Done with simulation')
