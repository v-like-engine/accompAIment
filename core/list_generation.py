from numpy import random as nprand


def calculate_probabilities(fitnesses, fitness_sum):
    """
    Method for calculating probabilities for probability-dependent choice for the roulette wheel in the parents'
    lists generation
    :param fitnesses: list of fitness values
    :param fitness_sum: sum of all the fitness values (for the fast access)
    :return: list of corresponding probabilities summing up to 1
    """
    probabilities = list(map(lambda x: x / fitness_sum, fitnesses))
    prob_sum = sum(probabilities)
    if prob_sum < 1:
        probabilities[-1] += 1 - prob_sum
    elif prob_sum > 1:
        diff = prob_sum - 1
        delta = diff / len(probabilities)
        probabilities = list(map(lambda x: x - delta, probabilities))
    return probabilities


def determine_parents_lists(generation: list, fitnesses, fitness_sum, n_of_children: int):
    """
    Method for generating n_of_children fathers and n_of_children mothers for the next crossovers
    They are chosen from the current generation by fitness proportional roulette wheel
    Parents do not repeat, and they are stored in random order, so they can be randomly breed pairwise by the index
    :param fitnesses: list of corresponding fitnesses of chromosomes from the generation
    :param generation: current generation, consisting
    :param fitness_sum: sum of all fitness values for the whole generation
    :param n_of_children: number of crossover applications = number of fathers = number of mothers
    :return: fathers list and mothers list
    """
    generation_cpy = generation.copy()
    fitness_cpy = fitnesses.copy()
    fitsum = fitness_sum
    probabilities = calculate_probabilities(fitness_cpy, fitsum)
    fathers = []
    mothers = []
    for i in range(n_of_children * 2):
        parent = nprand.choice(generation_cpy, 1, p=probabilities)[0]
        if i % 2 == 0:
            fathers.append(parent)
        else:
            mothers.append(parent)
        index = generation_cpy.index(parent)
        generation_cpy.remove(generation_cpy[index])
        probabilities.remove(probabilities[index])
        fitsum -= fitness_cpy[index]
        fitness_cpy.remove(fitness_cpy[index])
        probabilities = calculate_probabilities(fitness_cpy, fitsum)
    return fathers, mothers

