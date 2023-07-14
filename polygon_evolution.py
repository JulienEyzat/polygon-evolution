import random
import shapely
import shapely.affinity
import numpy as np
import matplotlib.pyplot as plt
import tqdm
import time

class Creature:
    def __init__(self, points=None):
        self._generate_itself(points)
        self.age = 0

    def _generate_itself(self, points):
        self.is_valid = True
        if not points:
            self.points = [shapely.Point((random.uniform(0, 10), random.uniform(0, 10))) for _ in range(7)]
            self.points = sorted(self.points, key=lambda k: k.x)
        else:
            self.points = points
        self.polygon = shapely.Polygon(self.points)
        if not self.polygon.is_valid:
            # If child, stop generation
            if points:
                self.is_valid = False
                return
            # If first generation, keep trying
            self._generate_itself(None)

    def is_creature_in_me(self, creature):
        for creature_point in creature.points:
            if self.polygon.contains(creature_point):
                return True
        return False

    def translate(self, x_translation=0, y_translation=0):
        self.points = [ shapely.affinity.translate(point, xoff=x_translation, yoff=y_translation) for point in self.points ]
        self.polygon = shapely.affinity.translate(self.polygon, xoff=x_translation, yoff=y_translation)

    def ages(self):
        self.age += 1

    def plot(self):
        x,y = self.polygon.exterior.xy
        plt.ylim((0, 10))
        plt.plot(x,y)

    def recenter(self):
        center = self.polygon.centroid
        dist_to_5 = 5 - center.y
        self.translate(y_translation=dist_to_5)

def set_pairs(creatures):
    creature_pairs = []
    for _ in range(len(creatures)//2):
        idx = random.randrange(0, len(creatures))
        creature1 = creatures.pop(idx)
        idx = random.randrange(0, len(creatures))
        creature2 = creatures.pop(idx)
        creature_pairs.append([creature1, creature2])
    return creature_pairs

def is_outside_arena(creature):
    for creature_point in creature.points:
        if creature_point.x < 0:
            return True
    return False

def plot_arena(creature_pair):
    creature_pair[0].plot()
    creature_pair[1].plot()
    plt.show()

def fight(creature_pair, winners):
    no_looser = True
    # Place creatures in arena
    creature_pair[1].translate(10)
    creature_pair[0].recenter()
    creature_pair[1].recenter()
    step = 0.5
    nb_steps = 0
    cpt = 0
    while no_looser:
        # Move creatures toward each other
        creature_pair[1].translate(-step)
        nb_steps+=1
        # plot_arena(creature_pair)
        # Check if there is a looser 
        creature_pair_0_lose = creature_pair[0].is_creature_in_me(creature_pair[1])
        creature_pair_1_lose = creature_pair[1].is_creature_in_me(creature_pair[0])
        if creature_pair_0_lose or creature_pair_1_lose:
            no_looser = False
            creature_pair[1].translate(-10+nb_steps*step)
            if not creature_pair_0_lose:
                winners.append(creature_pair[0])
            if not creature_pair_1_lose:
                winners.append(creature_pair[1])
        # Check if the fighter is outside the arena (normaly cannot happen)
        if is_outside_arena(creature_pair[1]):
            no_looser = False
    return winners

def fights(creature_pairs):
    winners = []
    for creature_pair in creature_pairs:
        winners = fight(creature_pair, winners)
    return winners

def set_child(father, mother):
    child_points = []
    for father_point, mother_point in zip(father.points, mother.points):
        x = np.mean((father_point.x, mother_point.x)) + random.uniform(-1, 1)
        if x < 0: x = 0
        if x > 10: x = 10
        y = np.mean((father_point.y, mother_point.y)) + random.uniform(-1, 1)
        if y < 0: y = 0
        if y > 10: y = 10
        child_points.append(shapely.Point((x, y)))
    child = Creature(child_points)
    if not child.is_valid:
        return None
    return child

def set_children(creatures, nb_creatures):
    while len(creatures) < nb_creatures:
        father = random.choice(creatures)
        mother = random.choice(creatures)
        child = set_child(father, mother)
        if child:
            creatures.append(child)
    return creatures

def game():
    tour_plot = 10
    nb_tours = 30
    nb_creatures = 50
    # Generate creatures
    creatures = [Creature() for _ in range(nb_creatures)]
    for i in tqdm.tqdm(range(nb_tours)):
        # Fight creatures
        creature_pairs = set_pairs(creatures)
        creature_winners = fights(creature_pairs)

        # Create n children
        creatures = set_children(creature_winners, nb_creatures)
        
        # Age
        [ creature.ages() for creature in creatures ]

        # Plot best creatures
        if i%tour_plot == 0:
            ages = [creature.age for creature in creatures]
            plt.hist(ages)
            plt.show()
            best_creatures = [ creature for creature in creatures if creature.age > 5 ]
            for best_creature in best_creatures[:5]:
                best_creature.plot()
                plt.show()

    # Plot each creature with ages
    ages = [creature.age for creature in creatures]
    plt.hist(ages)
    plt.show()
    for i in range(nb_creatures):
        print(creatures[i].age)
        creatures[i].plot()
        plt.show()

if __name__ == "__main__":
    game()