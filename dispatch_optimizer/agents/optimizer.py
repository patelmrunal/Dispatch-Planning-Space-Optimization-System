"""
optimizer.py
Core optimization logic for warehouse storage and inventory optimization using DEAP (Genetic Algorithm).
"""

from deap import base, creator, tools, algorithms
import random
import numpy as np

def optimize_dispatch(products, constraints):
    """
    Optimize storage layout and inventory placement using a genetic algorithm.
    Args:
        products (list of dict): List of product data.
        constraints (dict): Constraints for optimization.
    Returns:
        list of dict: Optimized storage plan.
    """
    # Problem parameters
    n = len(products)
    max_weight = constraints.get('max_storage_weight', float('inf'))
    max_volume = constraints.get('storage_length', float('inf')) * constraints.get('storage_width', float('inf')) * constraints.get('storage_height', float('inf'))
    volumes = [p['Length'] * p['Width'] * p['Height'] for p in products]
    weights = [p['Weight'] for p in products]

    # DEAP setup
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)
    toolbox = base.Toolbox()
    toolbox.register("indices", random.sample, range(n), n)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def eval_storage(individual):
        storage_areas = []
        current_area = []
        current_weight = 0
        current_volume = 0
        for idx in individual:
            w = weights[idx]
            v = volumes[idx]
            if current_weight + w > max_weight or current_volume + v > max_volume:
                storage_areas.append(current_area)
                current_area = []
                current_weight = 0
                current_volume = 0
            current_area.append(idx)
            current_weight += w
            current_volume += v
        if current_area:
            storage_areas.append(current_area)
        return (len(storage_areas),)  # Minimize number of storage areas

    toolbox.register("evaluate", eval_storage)
    toolbox.register("mate", tools.cxPartialyMatched)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=50)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", np.min)
    stats.register("avg", np.mean)

    algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=40, stats=stats, halloffame=hof, verbose=False)

    best = hof[0]
    # Assign storage order and area number
    storage_plan = [dict(products[i]) for i in best]
    # Assign storage area numbers
    area_num = 1
    current_weight = 0
    current_volume = 0
    for i, p in enumerate(storage_plan):
        w = p['Weight']
        v = p['Length'] * p['Width'] * p['Height']
        if current_weight + w > max_weight or current_volume + v > max_volume:
            area_num += 1
            current_weight = 0
            current_volume = 0
        p['StorageOrder'] = i + 1
        p['Storage Area #'] = area_num
        current_weight += w
        current_volume += v
    return storage_plan 