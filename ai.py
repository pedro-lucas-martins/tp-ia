import random
import numpy as np
import pickle
import os
from collections import defaultdict

class QLearningAgent:

    
    def __init__(self, learning_rate=0.2, discount_factor=0.95, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.05):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        self.q_table_file = "q_table.pkl"
        self.load_q_table()

    def decay_epsilon(self):
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def get_state_key(self, state):
        return str(state)
    
    def choose_action(self, state, possible_actions):
        
        state_key = self.get_state_key(state)
        
        if random.random() < self.epsilon:
            
            return random.choice(possible_actions)
        else:
            
            best_action = possible_actions[0]
            best_value = self.q_table[state_key][best_action]
            
            for action in possible_actions:
                value = self.q_table[state_key][action]
                if value > best_value:
                    best_value = value
                    best_action = action
            
            return best_action
    
    def update_q_value(self, state, action, reward, next_state, next_possible_actions):
        
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Valor Q atual
        current_q = self.q_table[state_key][action]
        
        # Melhor valor Q do próximo estado
        max_next_q = 0
        if next_possible_actions:
            max_next_q = max([self.q_table[next_state_key][a] for a in next_possible_actions])
        
        # Atualizar Q-value
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state_key][action] = new_q
    
    def save_q_table(self):
        try:
            with open(self.q_table_file, 'wb') as f:
                pickle.dump(dict(self.q_table), f)
        except Exception as e:
            print(f"Erro ao salvar tabela Q: {e}")
    
    def load_q_table(self):

        try:
            if os.path.exists(self.q_table_file):
                with open(self.q_table_file, 'rb') as f:
                    loaded_table = pickle.load(f)
                    self.q_table = defaultdict(lambda: defaultdict(float), loaded_table)
                print("Tabela Q carregada com sucesso")
        except Exception as e:
            print(f"Erro ao carregar tabela Q: {e}")
    
    def get_stats(self):
        
        total_states = len(self.q_table)
        total_actions = sum(len(actions) for actions in self.q_table.values())
        
        return {
            'total_states': total_states,
            'total_actions': total_actions,
            'epsilon': self.epsilon,
            'learning_rate': self.learning_rate
        }

class GeneticAlgorithmOptimizer:
    
    
    def __init__(self, population_size=20, mutation_rate=0.1, crossover_rate=0.7):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generation = 0
        self.best_fitness_history = []
        
    def create_individual(self, game_map):
        
        individual = {
            'towers': [],
            'fitness': 0
        }
        
        num_towers = random.randint(3, 8)
        
        for _ in range(num_towers):
            attempts = 0
            while attempts < 50:
                x = random.randint(0, game_map.width - 1)
                y = random.randint(0, game_map.height - 1)
                
                if game_map.can_place_tower(x, y):
                    tower_type = random.choice(['CANNON', 'MISSILE', 'LASER'])
                    individual['towers'].append({
                        'x': x,
                        'y': y,
                        'type': tower_type
                    })
                    break
                
                attempts += 1
        
        return individual
    
    def create_population(self, game_map):
        
        population = []
        for _ in range(self.population_size):
            individual = self.create_individual(game_map)
            population.append(individual)
        return population
    
    def evaluate_fitness(self, individual, simulation_results):
        
        fitness = 0
        
        # Fitness baseado nos resultados da simulação
        if simulation_results:
            # Recompensar por eliminar atacantes
            fitness += simulation_results.get('eliminated_attackers', 0) * 10
            
            # Penalizar por atacantes que passaram
            fitness -= simulation_results.get('successful_attackers', 0) * 5
            
            # Bônus por eficiência defensiva
            defense_efficiency = simulation_results.get('defense_efficiency', 0)
            fitness += defense_efficiency * 2
            
            # Penalizar por muitas torres (eficiência de recursos)
            num_towers = len(individual['towers'])
            if num_towers > 6:
                fitness -= (num_towers - 6) * 2
        
        # Bônus por cobertura estratégica
        coverage_bonus = self.calculate_coverage_bonus(individual)
        fitness += coverage_bonus
        
        individual['fitness'] = max(0, fitness)  # Fitness não pode ser negativo
        return individual['fitness']
    
    def calculate_coverage_bonus(self, individual):
        
        bonus = 0
        
        # Bonus por diversidade de tipos de torre
        tower_types = set(tower['type'] for tower in individual['towers'])
        bonus += len(tower_types) * 5
        
        # Bonus por distribuição espacial
        if len(individual['towers']) > 1:
            positions = [(tower['x'], tower['y']) for tower in individual['towers']]
            
            # Calcular distancia média entre torres
            total_distance = 0
            count = 0
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    x1, y1 = positions[i]
                    x2, y2 = positions[j]
                    distance = abs(x1 - x2) + abs(y1 - y2)
                    total_distance += distance
                    count += 1
            
            if count > 0:
                avg_distance = total_distance / count
                # Recompensar distribuição moderada 
                if 3 <= avg_distance <= 8:
                    bonus += 10
        
        return bonus
    
    def selection(self, population):
        
        selected = []
        tournament_size = 3
        
        for _ in range(len(population)):
            tournament = random.sample(population, min(tournament_size, len(population)))
            winner = max(tournament, key=lambda x: x['fitness'])
            selected.append(winner.copy())
        
        return selected
    
    def crossover(self, parent1, parent2):
        
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        child1 = {'towers': [], 'fitness': 0}
        child2 = {'towers': [], 'fitness': 0}
        
        # Combinar torres dos pais
        all_towers = parent1['towers'] + parent2['towers']
        
        # Remover duplicatas por posição
        unique_positions = {}
        for tower in all_towers:
            pos = (tower['x'], tower['y'])
            if pos not in unique_positions:
                unique_positions[pos] = tower
        
        unique_towers = list(unique_positions.values())
        
        # Distribuir torres entre os filhos
        for tower in unique_towers:
            if len(child1['towers']) < 8 and random.random() < 0.5:
                child1['towers'].append(tower.copy())
            elif len(child2['towers']) < 8:
                child2['towers'].append(tower.copy())
        
        return child1, child2
    
    def mutation(self, individual, game_map):
        
        mutated = individual.copy()
        mutated['towers'] = [tower.copy() for tower in individual['towers']]
        
        # Mutação de tipo de torre
        for tower in mutated['towers']:
            if random.random() < self.mutation_rate:
                tower['type'] = random.choice(['CANNON', 'MISSILE', 'LASER'])
        
        # Mutação de posição
        for tower in mutated['towers']:
            if random.random() < self.mutation_rate:
                attempts = 0
                while attempts < 20:
                    new_x = random.randint(0, game_map.width - 1)
                    new_y = random.randint(0, game_map.height - 1)
                    
                    if game_map.can_place_tower(new_x, new_y):
                        tower['x'] = new_x
                        tower['y'] = new_y
                        break
                    
                    attempts += 1
        
        # Adicionar nova torre
        if random.random() < self.mutation_rate and len(mutated['towers']) < 8:
            attempts = 0
            while attempts < 20:
                x = random.randint(0, game_map.width - 1)
                y = random.randint(0, game_map.height - 1)
                
                if game_map.can_place_tower(x, y):
                    tower_type = random.choice(['CANNON', 'MISSILE', 'LASER'])
                    mutated['towers'].append({
                        'x': x,
                        'y': y,
                        'type': tower_type
                    })
                    break
                
                attempts += 1
        
        # Remover torre
        if random.random() < self.mutation_rate and len(mutated['towers']) > 1:
            mutated['towers'].pop(random.randint(0, len(mutated['towers']) - 1))
        
        return mutated
    
    def evolve_generation(self, population, simulation_results, game_map):
        
        # Avaliar fitness
        for individual in population:
            self.evaluate_fitness(individual, simulation_results)
        
        # Registrar melhor fitness
        best_fitness = max(individual['fitness'] for individual in population)
        self.best_fitness_history.append(best_fitness)
        
        # Seleção
        selected = self.selection(population)
        
        # Crossover e mutação
        new_population = []
        for i in range(0, len(selected), 2):
            parent1 = selected[i]
            parent2 = selected[(i + 1) % len(selected)]
            
            child1, child2 = self.crossover(parent1, parent2)
            
            child1 = self.mutation(child1, game_map)
            child2 = self.mutation(child2, game_map)
            
            new_population.extend([child1, child2])
        
        self.generation += 1
        return new_population[:self.population_size]
    
    def get_best_individual(self, population):
        
        return max(population, key=lambda x: x['fitness'])
    
    def get_stats(self):
        
        return {
            'generation': self.generation,
            'population_size': self.population_size,
            'mutation_rate': self.mutation_rate,
            'crossover_rate': self.crossover_rate,
            'best_fitness_history': self.best_fitness_history
        }

class AIManager:
    
    
    def __init__(self):
        self.q_learning_agent = QLearningAgent()
        self.genetic_optimizer = GeneticAlgorithmOptimizer()
        self.tower_population = None
        
    def initialize_genetic_algorithm(self, game_map):
        
        self.tower_population = self.genetic_optimizer.create_population(game_map)
        print(f"População inicial criada com {len(self.tower_population)} indivíduos")
    
    def update_genetic_algorithm(self, simulation_results, game_map):
        
        if self.tower_population:
            self.tower_population = self.genetic_optimizer.evolve_generation(
                self.tower_population, simulation_results, game_map
            )
            
            best_individual = self.genetic_optimizer.get_best_individual(self.tower_population)
            print(f"Geração {self.genetic_optimizer.generation}: Melhor fitness = {best_individual['fitness']}")
            
            return best_individual
        return None
    
    def get_best_tower_layout(self):
        
        if self.tower_population:
            return self.genetic_optimizer.get_best_individual(self.tower_population)
        return None
    
    def save_ai_data(self):
        
        self.q_learning_agent.save_q_table()
        print("Dados de IA salvos")
    
    def get_ai_stats(self):
        
        return {
            'q_learning': self.q_learning_agent.get_stats(),
            'genetic_algorithm': self.genetic_optimizer.get_stats()
        }

