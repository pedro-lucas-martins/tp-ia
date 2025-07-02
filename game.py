import pygame
import random
import time
from enum import Enum
from map import GameMap, CellType
from agent import Attacker
from tower import Tower, TowerType
from ai import QLearningAgent
from agent import Attacker, AttackerState

class PlayerMode(Enum):
    SPECTATOR = "Espectador"
    ATTACKER = "Atacante"
    DEFENDER = "Defensor"

class Game:
    def setup_data_logger(self):
        from game_data_logger import GameDataLogger
        self.data_logger = GameDataLogger()
    def __init__(self, screen_width, screen_height, ui_instance):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui = ui_instance # Adiciona a instância da UI como atributo
        
        # Configurações do mapa
        self.map_width = 25
        self.map_height = 15
        self.cell_size = 40
        
        # Inicializar mapa
        self.game_map = GameMap(self.map_width, self.map_height, self.cell_size)
        
        # Listas de entidades
        self.attackers = []
        self.towers = []
        
        # Configurações do jogo
        self.player_mode = PlayerMode.SPECTATOR
        self.player_controlled_attacker = None
        self.current_tower_type_index = 0 # Índice para o tipo de torre atual
        self.tower_types_cycle = [TowerType.CANNON, TowerType.MISSILE, TowerType.LASER]
        self.max_towers = 4 # Limite máximo de torres
        
        # Estatísticas do jogo
        self.stats = {
            'active_attackers': 0,
            'eliminated_attackers': 0,
            'successful_attackers': 0,
            'towers': 0,
            'score': 0,
            'player_mode': self.player_mode.value
        }

        self.q_learning_agent = QLearningAgent(
            learning_rate=0.9,            # Valor aumentado para aprendizado mais rápido
            discount_factor=0.9,
            epsilon=1.0,
            epsilon_decay=0.9995,
            epsilon_min=0.05
        )

        # Controle de tempo
        self.game_start_time = 0
        self.last_attacker_spawn = 0
        self.attacker_spawn_interval = 2.0  # segundos
        #self.max_attackers = 10

        self.wave_total_attackers = 50 # Total de atacantes a serem gerados na partida
        self.wave_spawned_attackers = 0  # Contador de quantos já foram gerados
        
        # Estado do jogo
        self.game_running = False
        self.game_over = False
        
        # Configurações de IA
        self.ai_update_interval = 0.1  # segundos
        self.last_ai_update = 0
    
    def start_new_game(self):
        """Inicia um novo jogo"""
        print("Iniciando novo jogo...")
        
        # Resetar estado
        self.attackers.clear()
        self.towers.clear()
        self.game_over = False
        self.game_running = True
        
        # Resetar estatísticas
        self.stats = {
            'active_attackers': 0,
            'eliminated_attackers': 0,
            'successful_attackers': 0,
            'towers': 0,
            'score': 0,
            'player_mode': self.player_mode.value
        }
        
        # Configurar tempo
        self.game_start_time = time.time()
        self.last_attacker_spawn = self.game_start_time
        self.last_ai_update = self.game_start_time
        
        # Gerar novo mapa (opcional)
        if random.random() < 0.3:  # 30% de chance de mapa complexo
            self.game_map.generate_complex_map()
        else:
            self.game_map.generate_default_map()
        
        # Colocar algumas torres iniciais (modo espectador/defensor)
        # if self.player_mode != PlayerMode.ATTACKER:
        #     self.place_initial_towers()
        
        print(f"Jogo iniciado no modo: {self.player_mode.value}")
        # Inicializa logger de dados
        self.setup_data_logger()
    
    def place_initial_towers(self):
        
        initial_tower_count = random.randint(3, 6)
        towers_placed = 0
        attempts = 0
        max_attempts = 50
        
        while towers_placed < initial_tower_count and attempts < max_attempts:
            x = random.randint(0, self.map_width - 1)
            y = random.randint(0, self.map_height - 1)
            
            if self.game_map.can_place_tower(x, y):
                tower = Tower(x, y, self.game_map)
                self.towers.append(tower)
                self.game_map.place_tower(x, y)
                towers_placed += 1
            
            attempts += 1
        
        self.stats['towers'] = len(self.towers)
        print(f"Torres iniciais colocadas: {towers_placed}")
    
    def spawn_attacker(self):
        
        max_attempts = 20
        for _ in range(max_attempts):
            spawn_x = 0
            spawn_y = random.randint(0, self.map_height - 1)
            
            # Verifica se a célula é válida
            cell_type = self.game_map.get_cell(spawn_x, spawn_y)
            if cell_type in [CellType.PATH, CellType.START, CellType.EMPTY]:
                attacker = Attacker(spawn_x, spawn_y, self.game_map, self.q_learning_agent)
                self.attackers.append(attacker)
                self.stats["active_attackers"] = len(self.attackers)
                print(f"Atacante gerado em ({spawn_x}, {spawn_y})")
                return
        
        print("Aviso: Não foi encontrar posição de spawn válida")

    def save_ai_data(self):
        print("Salvando dados da IA...")
        self.q_learning_agent.save_q_table()
        print("Dados salvos com sucesso.")
    
    def update(self):
        
        if not self.game_running:
            return "idle"
    
        current_time = time.time()

        
        if hasattr(self, 'data_logger'):
            stats = self.get_game_stats()
            stats['time'] = current_time - self.game_start_time
            self.data_logger.log(stats, stats['time'])
    
        # Gerar atacantes periodicamente
        if current_time - self.last_attacker_spawn > self.attacker_spawn_interval:
            self.spawn_attacker()
            self.last_attacker_spawn = current_time
    
        # Atualizar atacantes
        attackers_to_remove = []
        for attacker in self.attackers:
            result = attacker.update()
    
            if result == "reached_end":
                attackers_to_remove.append(attacker)
                self.stats['successful_attackers'] += 1
                self.stats['score'] -= 10
                print("Atacante chegou ao destino!")
            elif result == "eliminated":
                attackers_to_remove.append(attacker)
                self.stats['eliminated_attackers'] += 1
                self.stats['score'] += 5
                print("Atacante eliminado!")
    
        # Remover atacantes que terminaram
        for attacker in attackers_to_remove:
            self.attackers.remove(attacker)
    
        self.stats['active_attackers'] = len(self.attackers)
    
        # Atualizar torres
        for tower in self.towers:
            target = tower.find_target(self.attackers)
            if target:
                damage_dealt = tower.attack(target)
                if damage_dealt > 0:
                    self.stats['score'] += 1
                    # Verifica se o alvo morreu após o ataque
                    if target.health <= 0:
                        self.stats['eliminated_attackers'] += 1
                        self.stats['score'] += 5
                        self.attackers.remove(target)
        
        # Atualizar IA periodicamente
        if current_time - self.last_ai_update > self.ai_update_interval:
            self.update_ai()
            self.last_ai_update = current_time

        self.q_learning_agent.decay_epsilon() # Reduz o epsilon a cada frame
        
        # Verificar condições de fim de jogo
        if self.check_game_over():
            self.game_over = True
            self.game_running = False
            # Plota e salva resultados ao final da partida
            if hasattr(self, 'data_logger'):
                self.data_logger.plot_results()
                self.data_logger.save_csv()
            return "game_over"
        
        return "playing"
    
    def update_ai(self):

        if self.player_mode != PlayerMode.DEFENDER:
            self.update_tower_ai()
    
    def update_tower_ai(self):
        if len(self.towers) < 8 and random.random() < 0.1:  # 10% de chance por update
            self.try_place_ai_tower()
    
    def try_place_ai_tower(self):
        
        from genetic_tower import TowerPlacementGA
        if len(self.towers) >= 4:
            return
        ga = TowerPlacementGA(self.game_map, num_towers=4)
        best_positions = ga.run(self.attackers)
        for x, y in best_positions:
            if self.game_map.can_place_tower(x, y) and len(self.towers) < 4:
                tower = Tower(x, y, self.game_map)
                self.towers.append(tower)
                self.game_map.place_tower(x, y)
                self.stats['towers'] = len(self.towers)
                print(f"IA colocou torre em ({x}, {y}) usando algoritmo genético")
    
    def check_game_over(self):
        
        if self.stats['successful_attackers'] >= 100:
            return True
        return False
    
    def handle_mouse_click(self, mouse_pos, button):
        
        # Converter posição do mouse para coordenadas da grade
        grid_x, grid_y = self.game_map.pixel_to_grid(mouse_pos[0], mouse_pos[1] - 60)
        
        if 0 <= grid_x < self.map_width and 0 <= grid_y < self.map_height:
            if self.player_mode == PlayerMode.DEFENDER:
                self.handle_defender_click(grid_x, grid_y, button)
            elif self.player_mode == PlayerMode.ATTACKER:
                self.handle_attacker_click(grid_x, grid_y, button)
    
    def handle_defender_click(self, grid_x, grid_y, button):
        
        if button == 1:  # Botão esquerdo - colocar torre
            if len(self.towers) < self.max_towers and self.game_map.can_place_tower(grid_x, grid_y):
                current_type = self.tower_types_cycle[self.current_tower_type_index]
                tower = Tower(grid_x, grid_y, self.game_map, tower_type=current_type)
                self.towers.append(tower)
                self.game_map.place_tower(grid_x, grid_y)
                self.stats["towers"] = len(self.towers)
                print(f"Torre {current_type["name"]} colocada em ({grid_x}, {grid_y})")
                
                # Ciclar para o próximo tipo de torre
                self.current_tower_type_index = (self.current_tower_type_index + 1) % len(self.tower_types_cycle)
        
        elif button == 3:  # Botão direito - remover torre
            if self.game_map.get_cell(grid_x, grid_y) == CellType.TOWER:
                # Encontrar e remover a torre
                for tower in self.towers[:]:
                    if tower.grid_x == grid_x and tower.grid_y == grid_y:
                        self.towers.remove(tower)
                        break
                
                self.game_map.remove_tower(grid_x, grid_y)
                self.stats['towers'] = len(self.towers)
                print(f"Torre removida de ({grid_x}, {grid_y})")
    
    def handle_attacker_click(self, grid_x, grid_y, button):
        
        if button == 1:  # Botão esquerdo - selecionar/mover atacante
            # Encontrar atacante mais próximo
            closest_attacker = None
            min_distance = float('inf')
            
            for attacker in self.attackers:
                distance = abs(attacker.grid_x - grid_x) + abs(attacker.grid_y - grid_y)
                if distance < min_distance:
                    min_distance = distance
                    closest_attacker = attacker
            
            if closest_attacker and min_distance <= 2:
                self.player_controlled_attacker = closest_attacker
                # Definir destino para o atacante
                closest_attacker.set_player_target(grid_x, grid_y)
                print(f"Atacante direcionado para ({grid_x}, {grid_y})")
    
    def set_player_mode(self, mode):
        
        self.player_mode = mode
        self.stats['player_mode'] = mode.value
        self.player_controlled_attacker = None
        print(f"Modo do jogador alterado para: {mode.value}")
    
    def get_game_stats(self):
        
        return self.stats.copy()
    
    def get_final_stats(self):
        
        total_attackers = self.stats['eliminated_attackers'] + self.stats['successful_attackers']
        defense_efficiency = 0
        if total_attackers > 0:
            defense_efficiency = (self.stats['eliminated_attackers'] / total_attackers) * 100
        
        game_duration = time.time() - self.game_start_time
        avg_survival_time = game_duration / max(total_attackers, 1)
        
        return {
            'eliminated_attackers': self.stats['eliminated_attackers'],
            'successful_attackers': self.stats['successful_attackers'],
            'defense_efficiency': defense_efficiency,
            'avg_survival_time': avg_survival_time,
            'final_score': self.stats['score']
        }
    
    def render(self, screen):
        
        # Renderizar mapa
        self.game_map.render(screen)
        
        # Renderizar atacantes
        for attacker in self.attackers:
            attacker.render(screen, offset_y=60)
            
            # Destacar atacante controlado pelo jogador
            if attacker == self.player_controlled_attacker:
                pixel_x, pixel_y = self.game_map.grid_to_pixel(attacker.grid_x, attacker.grid_y)
                pygame.draw.circle(screen, (255, 255, 0), (pixel_x, pixel_y + 60), 25, 3)
        
        # Renderizar torres
        for tower in self.towers:
            tower.render(screen, offset_y=60)
        
        # Renderizar alcance da torre selecionada (modo defensor)
        if self.player_mode == PlayerMode.DEFENDER:
            mouse_pos = pygame.mouse.get_pos()
            grid_x, grid_y = self.game_map.pixel_to_grid(mouse_pos[0], mouse_pos[1] - 60)
            
            # Mostrar onde uma nova torre seria colocada
            if (0 <= grid_x < self.map_width and 0 <= grid_y < self.map_height and 
                self.game_map.can_place_tower(grid_x, grid_y)):
                # Obter informações do tipo de torre (aleatório para demonstração)
                current_tower_type = self.tower_types_cycle[self.current_tower_type_index]
                
                self.ui.draw_tower_placement_indicator(screen, mouse_pos, current_tower_type, self.cell_size, self.map_width, self.map_height)