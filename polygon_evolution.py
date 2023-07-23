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
        self.nb_win = 0

    def _generate_itself(self, points):
        self.is_valid = True
        if not points:
            generated_points = [shapely.Point((random.uniform(0, 10), random.uniform(0, 10))) for _ in range(8)]
            generated_points = sorted(generated_points, key=lambda k: k.x)
        else:
            generated_points = points
        self.polygon = shapely.Polygon(generated_points)
        if not self.polygon.is_valid or not self.is_valid_points():
            # If child, stop generation
            if points:
                self.is_valid = False
                return
            # If first generation, keep trying
            self._generate_itself(None)

    def get_points(self):
        return [shapely.Point(coordinates) for coordinates in self.polygon.exterior.coords[:-1]]

    def is_creature_in_me(self, creature):
        for creature_point in creature.get_points():
            if self.polygon.contains(creature_point):
                return True
        return False

    def translate(self, x_translation=0, y_translation=0):
        self.polygon = shapely.affinity.translate(self.polygon, xoff=x_translation, yoff=y_translation)

    def rotate(self, rotation):
        self.polygon = shapely.affinity.rotate(self.polygon, rotation)

    def win(self):
        self.nb_win += 1

    def plot(self):
        x,y = self.polygon.exterior.xy
        plt.xlim((0, 10))
        plt.ylim((0, 10))
        plt.plot(x,y)

    def recenter(self):
        center = self.polygon.centroid
        x_dist_to_5 = 5 - center.x
        y_dist_to_5 = 5 - center.y
        self.translate(x_translation=x_dist_to_5)
        self.translate(y_translation=y_dist_to_5)

    def is_valid_points(self):
        self.recenter()
        for point in self.polygon.exterior.coords[:-1]:
            if point[0] > 10 or point[0] < 0: return False
            if point[1] > 10 or point[1] < 0: return False
        return True

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
    for creature_point in creature.get_points():
        if creature_point.x < 0:
            return True
    return False

def plot_arena(creature_pair):
    creature_pair[0].plot()
    creature_pair[1].plot()
    plt.show()

def fight(creature_pair):
    no_looser = True
    # Place creatures in arena
    creature_pair[0].recenter()
    creature_pair[1].recenter()
    creature_pair[1].translate(10)
    creature_pair[0].rotate(random.choice([0, 90, 180, 270]))
    creature_pair[1].rotate(random.choice([0, 90, 180, 270]))
    step = 1
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
                creature_pair[0].win()
            if not creature_pair_1_lose:
                creature_pair[1].win()
        # Check if the fighter is outside the arena (normaly cannot happen)
        if is_outside_arena(creature_pair[1]):
            no_looser = False
    creature_pair[0].recenter()
    creature_pair[1].recenter()
    return creature_pair

def fights(creature_pairs, nb_fights):
    creatures = []
    for creature_pair in creature_pairs:
        creature_pair[0].nb_win = 0
        creature_pair[1].nb_win = 0
        # Fight n times
        for _ in range(nb_fights):
            creature_pair = fight(creature_pair)
        creatures.append(creature_pair[0])
        creatures.append(creature_pair[1])
    # Select best winners
    creatures = sorted(creatures, key=lambda x: x.nb_win, reverse=True)
    winners = creatures[:10]
    return winners

def set_child(father, mother):
    child_points = []
    for father_point, mother_point in zip(father.get_points(), mother.get_points()):
        # Merge father and mother
        child_point = random.choice([father_point, mother_point])
        # Mutate
        if random.uniform(0, 1) < 0.2:
            xoff = random.uniform(-1, 1)
            yoff = random.uniform(-1, 1)
            child_point = shapely.affinity.translate(child_point, xoff=xoff, yoff=yoff)
        child_points.append(child_point)
    # Try to create child
    child = Creature(child_points)
    if not child.is_valid:
        return None
    return child

def set_children(creatures, nb_creatures):
    new_creatures = []
    while len(new_creatures) < nb_creatures:
        father = random.choice(creatures)
        mother = random.choice(creatures)
        child = set_child(father, mother)
        if child:
            new_creatures.append(child)
    return new_creatures

def game():
    tour_plot = 10
    nb_tours = 100
    nb_creatures = 50
    nb_fights = 5
    # Generate creatures
    creatures = [Creature() for _ in range(nb_creatures)]
    for i in tqdm.tqdm(range(nb_tours)):
        # Fight creatures
        creature_pairs = set_pairs(creatures)
        creatures = fights(creature_pairs, nb_fights)

        # Plot best creatures
        if i%tour_plot == 0:
            nb_wins = [creature.nb_win for creature in creatures]
            best_creatures = [ creature for creature in creatures if creature.nb_win == nb_fights ]
            for best_creature in best_creatures[:5]:
                best_creature.plot()
                plt.show()

        # Create n children
        if i < nb_tours-1:
            creatures = set_children(creatures, nb_creatures)

    # Plot each creature with ages
    nb_wins = [creature.nb_win for creature in creatures]
    for i in range(nb_creatures):
        print(creatures[i].nb_win)
        creatures[i].plot()
        plt.show()

if __name__ == "__main__":
    game()