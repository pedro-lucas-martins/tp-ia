import pygame
import math # Necessário para o cálculo de distância
import random
import time

class TowerType:
    CANNON = {
        'name': 'Canhão',
        'damage': 25,
        'range': 3,
        'attack_speed': 1.0,  # ataques por segundo
        'cost': 50,
        'color': (100, 100, 255)
    }
    
    MISSILE = {
        'name': 'Míssil',
        'damage': 40,
        'range': 4,
        'attack_speed': 0.5,
        'cost': 80,
        'color': (255, 100, 100)
    }
    
    LASER = {
        'name': 'Laser',
        'damage': 15,
        'range': 5,
        'attack_speed': 2.0,
        'cost': 70,
        'color': (100, 255, 100)
    }

class Tower:
    DEFAULT_RANGE = 3
    
    def __init__(self, grid_x, grid_y, game_map, tower_type=None):
        # Posição no mapa
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x, self.pixel_y = game_map.grid_to_pixel(grid_x, grid_y)
        
        # Referência ao mapa
        self.game_map = game_map
        
        # Tipo da torre (aleatório se não especificado)
        if tower_type is None:
            tower_types = [TowerType.CANNON, TowerType.MISSILE, TowerType.LASER]
            self.tower_type = random.choice(tower_types)
        else:
            self.tower_type = tower_type
        
        # Atributos da torre
        self.damage = self.tower_type['damage']
        self.range = self.tower_type['range']
        self.attack_speed = self.tower_type['attack_speed']
        self.cost = self.tower_type['cost']
        self.color = self.tower_type['color']
        
        # Estado de ataque
        self.last_attack_time = 0
        self.target = None
        self.attack_cooldown = 1.0 / self.attack_speed
        
        # Estatísticas
        self.total_damage_dealt = 0
        self.enemies_killed = 0
        self.shots_fired = 0
        
        # Algoritmo genético (fitness)
        self.fitness_score = 0
        self.generation = 0
        
        # Renderização
        self.size = 18
        self.range_color = (255, 255, 255, 50)  # Branco semi-transparente
    
    def calculate_distance(self, target):
        
        dx = abs(self.grid_x - target.grid_x)
        dy = abs(self.grid_y - target.grid_y)
        return math.sqrt(dx * dx + dy * dy)
    
    def is_in_range(self, target):
        
        distance = self.calculate_distance(target)
        return distance <= self.range
    
    def find_target(self, attackers):
        
        valid_targets = []
        
        # Filtrar atacantes no alcance
        for attacker in attackers:
            if self.is_in_range(attacker) and attacker.health > 0:
                valid_targets.append(attacker)
        
        if not valid_targets:
            self.target = None
            return None
        
        best_target = None
        min_distance_to_end = float('inf')
        
        # Se o mapa não tiver uma posição final definida, ataca o primeiro alvo válido
        if not self.game_map.end_pos:
            self.target = valid_targets[0]
            return self.target

        end_x, end_y = self.game_map.end_pos

        for attacker in valid_targets:
            # Calcular a distância euclidiana do atacante até o ponto final
            distance = math.sqrt((attacker.grid_x - end_x)**2 + (attacker.grid_y - end_y)**2)
            if distance < min_distance_to_end:
                min_distance_to_end = distance
                best_target = attacker
        
        self.target = best_target
        return best_target
    
    def can_attack(self):
        
        current_time = time.time()
        return current_time - self.last_attack_time >= self.attack_cooldown
    
    def attack(self, target):
        if not self.can_attack() or not target or target.health <= 0:
            return 0

        if not self.is_in_range(target):
            return 0

        damage_dealt = min(self.damage, target.health)  # Garante que não exceda a vida restante
        target.take_damage(damage_dealt)

        self.total_damage_dealt += damage_dealt
        self.shots_fired += 1
        self.last_attack_time = time.time()

        if target.health <= 0:
            self.enemies_killed += 1
            return damage_dealt  # Retorna o dano mesmo que o alvo morra

        return damage_dealt
    
    def update_fitness(self):
        
        # Fitness baseado em dano causado, inimigos mortos e eficiência
        damage_score = self.total_damage_dealt * 0.1
        kill_score = self.enemies_killed * 10
        efficiency_score = 0
        
        if self.shots_fired > 0:
            hit_rate = self.total_damage_dealt / (self.shots_fired * self.damage)
            efficiency_score = hit_rate * 5
        
        self.fitness_score = damage_score + kill_score + efficiency_score
    
    def get_fitness(self):
        
        return self.fitness_score
    
    def mutate(self):
        
        # Pequenas alterações nos atributos
        mutation_rate = 0.1
        
        if random.random() < mutation_rate:
            # Mutar tipo de torre
            tower_types = [TowerType.CANNON, TowerType.MISSILE, TowerType.LASER]
            self.tower_type = random.choice(tower_types)
            
            # Atualizar atributos
            self.damage = self.tower_type['damage']
            self.range = self.tower_type['range']
            self.attack_speed = self.tower_type['attack_speed']
            self.cost = self.tower_type['cost']
            self.color = self.tower_type['color']
            self.attack_cooldown = 1.0 / self.attack_speed
    
    def crossover(self, other_tower):
        
        # Combinar características de duas torres
        new_tower = Tower(self.grid_x, self.grid_y, self.game_map)
        
        # Escolher características aleatoriamente dos pais
        if random.random() < 0.5:
            new_tower.tower_type = self.tower_type
        else:
            new_tower.tower_type = other_tower.tower_type
        
        # Atualizar atributos
        new_tower.damage = new_tower.tower_type['damage']
        new_tower.range = new_tower.tower_type['range']
        new_tower.attack_speed = new_tower.tower_type['attack_speed']
        new_tower.cost = new_tower.tower_type['cost']
        new_tower.color = new_tower.tower_type['color']
        new_tower.attack_cooldown = 1.0 / new_tower.attack_speed
        
        new_tower.generation = max(self.generation, other_tower.generation) + 1
        
        return new_tower
    
    def get_stats(self):
        
        return {
            'type': self.tower_type['name'],
            'damage': self.damage,
            'range': self.range,
            'attack_speed': self.attack_speed,
            'total_damage': self.total_damage_dealt,
            'enemies_killed': self.enemies_killed,
            'shots_fired': self.shots_fired,
            'fitness': self.fitness_score,
            'generation': self.generation
        }
    
    def render(self, screen, offset_x=0, offset_y=0):
        
        # Desenhar a torre como um quadrado
        size = self.size
        rect = pygame.Rect(
            int(self.pixel_x + offset_x - size // 2),
            int(self.pixel_y + offset_y - size // 2),
            size,
            size
        )
        
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)
        
        # Desenhar símbolo do tipo
        font = pygame.font.Font(None, 16)
        symbol = self.tower_type['name'][0]  # Primeira letra
        text = font.render(symbol, True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        
        # Desenhar linha de ataque se há um alvo
        if self.target and self.target.health > 0:
            start_pos = (int(self.pixel_x + offset_x), int(self.pixel_y + offset_y))
            end_pos = (int(self.target.pixel_x + offset_x), int(self.target.pixel_y + offset_y))
            
            # Cor da linha baseada no tipo de torre
            line_color = self.color
            pygame.draw.line(screen, line_color, start_pos, end_pos, 3)
    
    def render_range(self, screen, offset_x=0, offset_y=0):
        
        range_radius = self.range * self.game_map.cell_size
        center = (int(self.pixel_x + offset_x), int(self.pixel_y + offset_y))
        
        # Criar superfície transparente para o alcance
        range_surface = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, self.range_color, (range_radius, range_radius), range_radius)
        
        # Desenhar na tela
        screen.blit(range_surface, (center[0] - range_radius, center[1] - range_radius))
        
        # Desenhar borda do alcance
        pygame.draw.circle(screen, (255, 255, 255), center, range_radius, 1)

class GeneticAlgorithm:
    
    
    def __init__(self, game_map):
        self.game_map = game_map
        self.population_size = 20
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.generation = 0
        
    def create_random_tower_layout(self):
        
        towers = []
        num_towers = random.randint(5, 10)
        
        for _ in range(num_towers):
            attempts = 0
            while attempts < 50:  # Evitar loop infinito
                x = random.randint(0, self.game_map.width - 1)
                y = random.randint(0, self.game_map.height - 1)
                
                if self.game_map.can_place_tower(x, y):
                    tower = Tower(x, y, self.game_map)
                    towers.append(tower)
                    break
                
                attempts += 1
        
        return towers
    
    def evaluate_fitness(self, tower_layout, simulation_results):
        
        total_fitness = 0
        
        for tower in tower_layout:
            tower.update_fitness()
            total_fitness += tower.get_fitness()
        
        # Adicionar bônus baseado nos resultados da simulação
        if simulation_results:
            defense_efficiency = simulation_results.get('defense_efficiency', 0)
            total_fitness += defense_efficiency * 2
        
        return total_fitness
    
    def selection(self, population, fitness_scores):
        
        selected = []
        tournament_size = 3
        
        for _ in range(len(population)):
            tournament = random.sample(list(zip(population, fitness_scores)), tournament_size)
            winner = max(tournament, key=lambda x: x[1])
            selected.append(winner[0])
        
        return selected
    
    def crossover(self, parent1, parent2):
        
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        # Combinar torres dos dois pais
        child1_towers = []
        child2_towers = []
        
        # Pegar torres de ambos os pais aleatoriamente
        all_positions = set()
        for tower in parent1 + parent2:
            all_positions.add((tower.grid_x, tower.grid_y))
        
        for pos in all_positions:
            if self.game_map.can_place_tower(pos[0], pos[1]):
                # Encontrar torres nesta posição
                towers_at_pos = []
                for tower in parent1 + parent2:
                    if (tower.grid_x, tower.grid_y) == pos:
                        towers_at_pos.append(tower)
                
                if towers_at_pos:
                    # Escolher aleatoriamente para cada filho
                    if random.random() < 0.5 and len(child1_towers) < 10:
                        selected_tower = random.choice(towers_at_pos)
                        new_tower = Tower(pos[0], pos[1], self.game_map, selected_tower.tower_type)
                        child1_towers.append(new_tower)
                    
                    if random.random() < 0.5 and len(child2_towers) < 10:
                        selected_tower = random.choice(towers_at_pos)
                        new_tower = Tower(pos[0], pos[1], self.game_map, selected_tower.tower_type)
                        child2_towers.append(new_tower)
        
        return child1_towers, child2_towers
    
    def mutation(self, tower_layout):
        
        for tower in tower_layout:
            if random.random() < self.mutation_rate:
                tower.mutate()
        
        # Adicionar/remover torres aleatoriamente
        if random.random() < self.mutation_rate:
            if len(tower_layout) > 1 and random.random() < 0.5:
                # Remover torre aleatória
                tower_layout.pop(random.randint(0, len(tower_layout) - 1))
            elif len(tower_layout) < 10:
                # Adicionar nova torre
                attempts = 0
                while attempts < 20:
                    x = random.randint(0, self.game_map.width - 1)
                    y = random.randint(0, self.game_map.height - 1)
                    
                    if self.game_map.can_place_tower(x, y):
                        new_tower = Tower(x, y, self.game_map)
                        tower_layout.append(new_tower)
                        break
                    
                    attempts += 1
        
        return tower_layout
    
    def evolve_generation(self, population, simulation_results):
        
        # Avaliar fitness
        fitness_scores = []
        for layout in population:
            fitness = self.evaluate_fitness(layout, simulation_results)
            fitness_scores.append(fitness)
        
        # Seleção
        selected = self.selection(population, fitness_scores)
        
        # Crossover e mutação
        new_population = []
        for i in range(0, len(selected), 2):
            parent1 = selected[i]
            parent2 = selected[(i + 1) % len(selected)]
            
            child1, child2 = self.crossover(parent1, parent2)
            
            child1 = self.mutation(child1)
            child2 = self.mutation(child2)
            
            new_population.extend([child1, child2])
        
        self.generation += 1
        return new_population[:self.population_size]