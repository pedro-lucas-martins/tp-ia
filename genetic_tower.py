import random

class TowerPlacementGA:
    def __init__(self, game_map, num_towers=4, population_size=20, generations=10, mutation_rate=0.1):
        self.game_map = game_map
        self.num_towers = num_towers
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    def random_individual(self):
        positions = []
        attempts = 0
        while len(positions) < self.num_towers and attempts < 100:
            x = random.randint(0, self.game_map.width - 1)
            y = random.randint(0, self.game_map.height - 1)
            if self.game_map.can_place_tower(x, y):
                start = self.game_map.start_pos
                end = self.game_map.end_pos
                too_close_to_start = start and (abs(x - start[0]) + abs(y - start[1]) < 4)
                too_close_to_end = end and (abs(x - end[0]) + abs(y - end[1]) < 4)
                if not too_close_to_start and not too_close_to_end and (x, y) not in positions:
                    positions.append((x, y))
            attempts += 1
        return positions

    def fitness(self, individual, attackers):
        covered = set()
        for tower_x, tower_y in individual:
            for attacker in attackers:
                dist = abs(attacker.grid_x - tower_x) + abs(attacker.grid_y - tower_y)
                if dist <= 2:
                    covered.add(attacker)
        return len(covered)

    def crossover(self, parent1, parent2):
        split = self.num_towers // 2
        child = parent1[:split] + [pos for pos in parent2 if pos not in parent1][:self.num_towers - split]
        return child

    def mutate(self, individual):
        if random.random() < self.mutation_rate:
            idx = random.randint(0, self.num_towers - 1)
            new_pos = self.random_individual()[0]
            individual[idx] = new_pos
        return individual

    def run(self, attackers):
        population = [self.random_individual() for _ in range(self.population_size)]
        for gen in range(self.generations):
            scored = [(self.fitness(ind, attackers), ind) for ind in population]
            scored.sort(reverse=True, key=lambda x: x[0])
            next_gen = [ind for _, ind in scored[:self.population_size // 2]]
            while len(next_gen) < self.population_size:
                parents = random.sample(next_gen, 2)
                child = self.crossover(parents[0], parents[1])
                child = self.mutate(child)
                next_gen.append(child)
            population = next_gen
        best = max(population, key=lambda ind: self.fitness(ind, attackers))
        return best
