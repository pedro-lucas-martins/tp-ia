import pygame
import random
from enum import Enum

class CellType(Enum):
    EMPTY = 0
    PATH = 1
    OBSTACLE = 2
    START = 3
    END = 4
    TOWER = 5

class GameMap:
    def __init__(self, width, height, cell_size=40):
        self.width = width  # Número de células na largura
        self.height = height  # Número de células na altura
        self.cell_size = cell_size  # Tamanho de cada célula em pixels
        
        # Matriz do mapa
        self.grid = [[CellType.EMPTY for _ in range(width)] for _ in range(height)]
        
        # Cores para renderização
        self.colors = {
            CellType.EMPTY: (50, 50, 50),      # Cinza escuro
            CellType.PATH: (100, 100, 100),    # Cinza
            CellType.OBSTACLE: (139, 69, 19),  # Marrom (obstáculos)
            CellType.START: (0, 255, 0),       # Verde (início)
            CellType.END: (255, 0, 0),         # Vermelho (fim)
            CellType.TOWER: (0, 0, 255)        # Azul (torres)
        }
        
        # Posições especiais
        self.start_pos = None
        self.end_pos = None
        self.path_points = []
        
        # Gerar mapa padrão
        self.generate_default_map()
    
    def generate_default_map(self):
        
        # 1. Limpa o grid e a lista de pontos do caminho
        self.grid = [[CellType.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        self.path_points = []

        # 2. Define um caminho horizontal simples no meio do mapa
        path_y = self.height // 2
        
        for x in range(self.width):
            self.set_cell(x, path_y, CellType.PATH)
            self.path_points.append((x, path_y)) # <-- Ponto crucial: preenche a lista

        # 3. Define o início e o fim nesse caminho
        self.start_pos = (0, path_y)
        self.set_cell(0, path_y, CellType.START)
        
        # Encontre o ponto final na última coluna
        end_point = None
        for y_coord in range(self.height):
            if (self.width -1, y_coord) in self.path_points:
                end_point = (self.width -1, y_coord)
                break
        
        if end_point:
            self.end_pos = end_point
            self.set_cell(self.end_pos[0], self.end_pos[1], CellType.END)


        # 4. Adiciona obstáculos aleatórios
        self.add_random_obstacles(15)

    def generate_complex_map(self):
        
        self.grid = [[CellType.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        
        self.start_pos = (0, random.randint(1, self.height-2))
        self.end_pos = (self.width - 1, random.randint(1, self.height-2))
        
        self.path_points = self._find_path_A_star(self.start_pos, self.end_pos)
        
        if not self.path_points:
            # Fallback para um caminho simples se o A* falhar
            self.generate_default_map()
            return
            
        for x, y in self.path_points:
            self.set_cell(x, y, CellType.PATH)
            
        self.set_cell(self.start_pos[0], self.start_pos[1], CellType.START)
        self.set_cell(self.end_pos[0], self.end_pos[1], CellType.END)
        
        self.add_random_obstacles(25)

    def add_random_obstacles(self, count):
        
        obstacles_added = 0
        attempts = 0
        max_attempts = count * 20
        
        while obstacles_added < count and attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            # Garante que o obstáculo não seja colocado no caminho, início ou fim
            if self.get_cell(x, y) == CellType.EMPTY:
                self.set_cell(x, y, CellType.OBSTACLE)
                obstacles_added += 1
            
            attempts += 1
            
    def _find_path_A_star(self, start, end):
        path = []
        x, y = start
        while (x, y) != end:
            path.append((x,y))
            if x < end[0]:
                x += 1
            elif x > end[0]:
                x -= 1
            
            if y < end[1]:
                y += 1
            elif y > end[1]:
                y -=1
        path.append(end)
        return path
    
    def can_place_obstacle(self, x, y):
        
        # Não pode colocar em células de início, fim ou torre
        current_cell = self.get_cell(x, y)
        return current_cell not in [CellType.START, CellType.END, CellType.TOWER]
    
    def can_place_tower(self, x, y):

        # Torres podem ser colocadas em células vazias ou de caminho
        current_cell = self.get_cell(x, y)
        return current_cell in [CellType.EMPTY, CellType.PATH]
    
    def place_tower(self, x, y):
        if self.can_place_tower(x, y):
            self.set_cell(x, y, CellType.TOWER)
            return True
        return False
    
    def remove_tower(self, x, y):
        
        if self.get_cell(x, y) == CellType.TOWER:
            self.set_cell(x, y, CellType.PATH)
            return True
        return False
    
    def get_cell(self, x, y):
        
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
    
    def set_cell(self, x, y, cell_type):
        
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = cell_type
    
    def get_neighbors(self, x, y):
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Cima, Direita, Baixo, Esquerda
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                cell_type = self.get_cell(nx, ny)
                if cell_type not in [CellType.OBSTACLE, CellType.TOWER]:
                    neighbors.append((nx, ny))
        
        return neighbors
    
    def get_valid_neighbors(self, x, y):
        neighbors = []
        # 8 direções (incluindo diagonais)
        directions = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                cell_type = self.get_cell(nx, ny)
                if cell_type not in [CellType.OBSTACLE, CellType.TOWER]:
                    neighbors.append((nx, ny))
        return neighbors
    
    def pixel_to_grid(self, pixel_x, pixel_y):
        
        grid_x = pixel_x // self.cell_size
        grid_y = pixel_y // self.cell_size
        return grid_x, grid_y
    
    def grid_to_pixel(self, grid_x, grid_y):
        
        pixel_x = grid_x * self.cell_size + self.cell_size // 2
        pixel_y = grid_y * self.cell_size + self.cell_size // 2
        return pixel_x, pixel_y
    
    def render(self, screen, offset_x=0, offset_y=60):
        
        for y in range(self.height):
            for x in range(self.width):
                cell_type = self.grid[y][x]
                color = self.colors[cell_type]
                
                # Calcular posição do retângulo
                rect = pygame.Rect(
                    offset_x + x * self.cell_size,
                    offset_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Desenhar célula
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)  # Borda branca
                
                # Adicionar símbolos para células especiais
                if cell_type == CellType.START:
                    self.draw_symbol(screen, rect, "S", (255, 255, 255))
                elif cell_type == CellType.END:
                    self.draw_symbol(screen, rect, "E", (255, 255, 255))
                elif cell_type == CellType.TOWER:
                    self.draw_symbol(screen, rect, "T", (255, 255, 255))
    
    def draw_symbol(self, screen, rect, symbol, color):
        
        font = pygame.font.Font(None, 24)
        text = font.render(symbol, True, color)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
    
    def get_path_length(self):
        
        return len(self.path_points)
    
    def get_next_path_point(self, current_index):
        
        if current_index < len(self.path_points) - 1:
            return self.path_points[current_index + 1]
        return None



