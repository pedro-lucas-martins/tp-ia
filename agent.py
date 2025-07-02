import pygame
from enum import Enum
from collections import deque
from map import CellType

class AttackerState(Enum):
    MOVING = 1
    ATTACKING = 2
    ELIMINATED = 3
    REACHED_END = 4

class Attacker:
    def __init__(self, start_x, start_y, game_map, q_learning_agent):
        self.grid_x = start_x
        self.grid_y = start_y
        self.pixel_x, self.pixel_y = game_map.grid_to_pixel(start_x, start_y)
        self.game_map = game_map
        self.stuck_time = 0
        self.max_stuck_time = 2  # inimigos eliminados mais rápido se ficarem presos
        self.stuck_penalty = -10  # penalidade mais forte por ficar parado
        self.last_position = None

        self.max_health = 100
        self.health = self.max_health
        self.speed = 1.0
        self.damage = 10
        self.state = AttackerState.MOVING

        self.observed_attacks = {}  # Registra posicoes perigosas

        # Armazena a referência ao agente de IA compartilhado
        self.q_agent = q_learning_agent
        self.last_state = None
        self.last_action = None

        self.player_controlled = False
        self.player_target = None

        self.last_positions = deque(maxlen=12)  # Evita loops mais longos
        self.last_distance = float('inf')  # Para calcular progresso
        
        self.color = (255, 100, 100)
        self.size = 15

        self.stuck_time = 0  # Tempo que o atacante está preso
        self.max_stuck_time = 5  # 5 segundos max preso antes de ser removido

    def get_state(self):
        
        features = []

        
        if self.game_map.path_points:
            path_dist = abs(self.grid_y - self.game_map.path_points[-1][1])
            features.append(min(path_dist, 5))  # Normalizado até 5

        
        danger_level = 0
        for dx in [-2,-1,0,1,2]:
            for dy in [-2,-1,0,1,2]:
                nx, ny = self.grid_x + dx, self.grid_y + dy
                if (0 <= nx < self.game_map.width and 
                    0 <= ny < self.game_map.height):
                    if self.game_map.get_cell(nx, ny).name == 'TOWER':
                        danger_level += 1 / (abs(dx) + abs(dy) + 1)  # Peso inverso à distância

        features.append(min(int(danger_level*10), 10))  

        
        if self.game_map.end_pos:
            end_x, end_y = self.game_map.end_pos
            features.append(1 if end_x > self.grid_x else -1)  # Direção horizontal
            features.append(1 if end_y > self.grid_y else -1)  # Direção vertical

        
        features.append(int((self.health / self.max_health) * 10))

        return tuple(features)

    def get_possible_actions(self):
        actions = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)] # Cima, Direita, Baixo, Esquerda
        for i, (dx, dy) in enumerate(directions):
            new_x, new_y = self.grid_x + dx, self.grid_y + dy
            if 0 <= new_x < self.game_map.width and 0 <= new_y < self.game_map.height:
                cell_type = self.game_map.get_cell(new_x, new_y)
                if cell_type and cell_type.name not in ['OBSTACLE', 'TOWER']:
                    actions.append(i)
        return actions

    def execute_action(self, action):
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        dx, dy = directions[action]
        new_x, new_y = self.grid_x + dx, self.grid_y + dy
        
        if (0 <= new_x < self.game_map.width and 
            0 <= new_y < self.game_map.height and
            self.game_map.get_cell(new_x, new_y) not in [CellType.OBSTACLE, CellType.TOWER] and
            (new_x, new_y) not in self.last_positions):
            
            self.grid_x, self.grid_y = new_x, new_y
            self.pixel_x, self.pixel_y = self.game_map.grid_to_pixel(new_x, new_y)
            self.last_positions.append((new_x, new_y))
            return True
        
        return False

    def calculate_reward(self):
    
        reward = 0
    
        # Penalidade por ficar parado
        if self.stuck_time > 0:
            reward += self.stuck_penalty * self.stuck_time

        # Penalidade extra se ficar muito tempo parado
        if self.stuck_time > 1:  # 1 segundo parado
            reward -= 50  # penalidade extra mais forte

        # Penalidade por revisitar posições recentes (loop)
        pos_count = self.last_positions.count((self.grid_x, self.grid_y))
        if pos_count > 1:
            reward -= 30 * (pos_count - 1)  # Penalidade proporcional ao numero de repeticoes

        # Recompensa por progresso
        if self.game_map.end_pos:
            end_x, end_y = self.game_map.end_pos
            dist = abs(end_x - self.grid_x) + abs(end_y - self.grid_y)
            reward += (self.last_distance - dist) * 2  # Recompensa por se aproximar
            self.last_distance = dist
        
        # Penalidades por perigo e permanecia em torres
        adjacent_tower_count = 0
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:  # 4 direcoes proximas
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if (0 <= nx < self.game_map.width and 
                0 <= ny < self.game_map.height):
                if self.game_map.get_cell(nx, ny).name == 'TOWER':
                    reward -= 15  # Penalidade por se aproximar de torres
                    adjacent_tower_count += 1

        # Penalidade extra se ficar várias iterações próximo de torre
        if adjacent_tower_count > 0:
            if not hasattr(self, 'adjacent_tower_time'):
                self.adjacent_tower_time = 0
            self.adjacent_tower_time += 1/60
            if self.adjacent_tower_time > 1:  # 1 segundo perto de torre
                reward -= 40 * self.adjacent_tower_time  # Penalidade progressiva
        else:
            self.adjacent_tower_time = 0
        
        # Bônus/penalidades globais
        if self.state == AttackerState.REACHED_END:
            reward += 500  # Recompensa aumentada por chegar ao fim
        elif self.state == AttackerState.ELIMINATED:
            reward -= 200
        return reward
    
    def tactical_retreat(self):
        if self.health < self.max_health * 0.3:
            directions = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
            safe_directions = []
            max_safety = float('-inf')
            best_dir = None
            for dx, dy in directions:
                nx, ny = self.grid_x + dx, self.grid_y + dy
                if (0 <= nx < self.game_map.width and 
                    0 <= ny < self.game_map.height):
                    cell = self.game_map.get_cell(nx, ny)
                    if cell not in [CellType.TOWER, CellType.OBSTACLE]:
                        safety = self._tower_avoidance((dx, dy))
                        if safety > max_safety:
                            max_safety = safety
                            best_dir = (dx, dy)
            if best_dir is not None:
                # Retorna a direção mais segura entre as 4, ou a mais próxima
                basic_dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
                if best_dir in basic_dirs:
                    return basic_dirs.index(best_dir)
                else:
                    # Se for diagonal, retorna a direcao mais próxima
                    closest = min(enumerate(basic_dirs), key=lambda t: abs(t[1][0]-best_dir[0])+abs(t[1][1]-best_dir[1]))
                    return closest[0]
        return None

    def _tower_avoidance(self, direction):
        
        dx, dy = direction
        safety = 0
        for x in range(max(0, self.grid_x-3), min(self.game_map.width, self.grid_x+4)):
            for y in range(max(0, self.grid_y-3), min(self.game_map.height, self.grid_y+4)):
                if self.game_map.get_cell(x, y).name == 'TOWER':
                    dist = abs((self.grid_x+dx) - x) + abs((self.grid_y+dy) - y)
                    safety += dist * 2
        return safety

    def update(self):
        if self.state in [AttackerState.ELIMINATED, AttackerState.REACHED_END]:
            return self.state.name.lower()

        current_pos = (self.grid_x, self.grid_y)

        
        if not hasattr(self, 'last_position'):
            self.last_position = current_pos
            self.stuck_time = 0

        
        is_stuck = (current_pos == self.last_position) or (self.last_positions and current_pos in self.last_positions)

        if is_stuck:
            self.stuck_time += 1/60  
            # Penalidade progressiva
            if hasattr(self, 'last_action'):
                penalty = self.stuck_penalty * (1 + self.stuck_time)
                self.q_agent.update_q_value(
                    self.get_state(),
                    self.last_action,
                    penalty,
                    self.get_state(),
                    self.get_possible_actions()
                )
            if self.stuck_time > self.max_stuck_time:
                print(f"Atacante eliminado por inatividade em {current_pos}")
                self.state = AttackerState.ELIMINATED
                return "eliminated"
        else:
            self.stuck_time = 0

        self.last_position = current_pos
        self.last_positions.append(current_pos)

        
        tactical_action = self.tactical_retreat()
        if tactical_action is not None:
            self.execute_action(tactical_action)
            return "retreating"

        current_state = self.get_state()
        possible_actions = self.get_possible_actions()

        if not possible_actions:
            # Tenta qualquer direção livre, mesmo que já tenha passado por lá
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            for i, (dx, dy) in enumerate(directions):
                new_x, new_y = self.grid_x + dx, self.grid_y + dy
                if 0 <= new_x < self.game_map.width and 0 <= new_y < self.game_map.height:
                    cell = self.game_map.get_cell(new_x, new_y)
                    if cell.name not in ['OBSTACLE', 'TOWER']:
                        # Permite repetir posição para destravar
                        self.grid_x, self.grid_y = new_x, new_y
                        self.pixel_x, self.pixel_y = self.game_map.grid_to_pixel(new_x, new_y)
                        self.last_positions.append((new_x, new_y))
                        break
            return

        # O agente de IA escolhe a ação
        action = self.q_agent.choose_action(current_state, possible_actions)

        # Atualiza a tabela Q com a experiência anterior
        if self.last_state is not None:
            reward = self.calculate_reward()
            self.q_agent.update_q_value(self.last_state, self.last_action, reward, current_state, possible_actions)

        # Executa a acao escolhida
        self.execute_action(action)

        # Salva o estado e ação
        self.last_state = self.get_state()
        self.last_action = action

        # Verifica o resultado do movimento
        current_cell_type = self.game_map.get_cell(self.grid_x, self.grid_y)
        if current_cell_type and current_cell_type.name == 'END':
            self.state = AttackerState.REACHED_END

        if self.health <= 0:
            self.state = AttackerState.ELIMINATED

    def take_damage(self, damage):
        self.health -= damage
        # Registra posição perigosa
        pos_key = (self.grid_x, self.grid_y)
        self.observed_attacks[pos_key] = self.observed_attacks.get(pos_key, 0) + 1
        
        if self.health <= 0:
            self.health = 0
            self.state = AttackerState.ELIMINATED
            return True
        return False

    def render(self, screen, offset_y=60):
        pygame.draw.circle(screen, self.color, (int(self.pixel_x), int(self.pixel_y + offset_y)), self.size)
        if self.health < self.max_health:
            bar_width = 30
            bar_height = 4
            bar_x = int(self.pixel_x - bar_width // 2)
            bar_y = int(self.pixel_y + offset_y - self.size - 8)
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
