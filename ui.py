import pygame
import math

class UI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Cores
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        self.LIGHT_GRAY = (192, 192, 192)
        self.YELLOW = (255, 255, 0)
        self.ORANGE = (255, 165, 0)
        
        # Fontes
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Estado do menu
        self.show_mode_selection = False
        
        # Botões do menu principal
        self.menu_buttons = {
            "start": pygame.Rect(screen_width//2 - 100, screen_height//2 - 50, 200, 50),
            "quit": pygame.Rect(screen_width//2 - 100, screen_height//2 + 20, 200, 50)
        }
        
        # Botões de seleção de modo
        self.mode_buttons = {
            "spectator": pygame.Rect(screen_width//2 - 150, screen_height//2 - 80, 300, 40),
            "attacker": pygame.Rect(screen_width//2 - 150, screen_height//2 - 30, 300, 40),
            "defender": pygame.Rect(screen_width//2 - 150, screen_height//2 + 20, 300, 40),
            "back": pygame.Rect(screen_width//2 - 100, screen_height//2 + 80, 200, 40)
        }
    
    def draw_menu(self, screen):
        
        if self.show_mode_selection:
            self.draw_mode_selection(screen)
        else:
            self.draw_main_menu(screen)
    
    def draw_main_menu(self, screen):
        """Desenha o menu principal"""
        # Título
        title_text = self.font_large.render("Jogo", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 150))
        screen.blit(title_text, title_rect)
        
        subtitle_text = self.font_medium.render("Tower Defense com IA", True, self.LIGHT_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 110))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Botões
        for button_name, button_rect in self.menu_buttons.items():
            # Desenhar botão
            pygame.draw.rect(screen, self.DARK_GRAY, button_rect)
            pygame.draw.rect(screen, self.WHITE, button_rect, 2)
            
            # Texto do botão
            if button_name == "start":
                button_text = "Iniciar Jogo"
            elif button_name == "quit":
                button_text = "Sair"
            
            text_surface = self.font_medium.render(button_text, True, self.WHITE)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
        
        # Instruções
        instructions = [
            "Pressione ESPAÇO para começar",
            "ESC para pausar/sair",
            "Mouse para interagir"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, self.GRAY)
            text_rect = text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 120 + i * 25))
            screen.blit(text, text_rect)
    
    def draw_mode_selection(self, screen):
        
        # Título
        title_text = self.font_large.render("Escolha seu Papel", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 150))
        screen.blit(title_text, title_rect)
        
        # Botões de modo
        mode_descriptions = {
            "spectator": "Espectador - Observe a IA em ação",
            "attacker": "Atacante - Controle um invasor",
            "defender": "Defensor - Posicione torres"
        }
        
        for button_name, button_rect in self.mode_buttons.items():
            if button_name == "back":
                # Botão voltar
                pygame.draw.rect(screen, self.DARK_GRAY, button_rect)
                pygame.draw.rect(screen, self.WHITE, button_rect, 2)
                
                text_surface = self.font_medium.render("Voltar", True, self.WHITE)
                text_rect = text_surface.get_rect(center=button_rect.center)
                screen.blit(text_surface, text_rect)
            else:
                # Botões de modo
                pygame.draw.rect(screen, self.DARK_GRAY, button_rect)
                pygame.draw.rect(screen, self.WHITE, button_rect, 2)
                
                # Texto do modo
                mode_text = mode_descriptions[button_name]
                text_surface = self.font_small.render(mode_text, True, self.WHITE)
                text_rect = text_surface.get_rect(center=button_rect.center)
                screen.blit(text_surface, text_rect)
    
    def handle_menu_click(self, mouse_pos):
        
        if self.show_mode_selection:
            return self.handle_mode_selection_click(mouse_pos)
        else:
            return self.handle_main_menu_click(mouse_pos)
    
    def handle_main_menu_click(self, mouse_pos):
        
        for button_name, button_rect in self.menu_buttons.items():
            if button_rect.collidepoint(mouse_pos):
                if button_name == "start":
                    self.show_mode_selection = True
                    return None
                else:
                    return button_name
        return None
    
    def handle_mode_selection_click(self, mouse_pos):
        
        for button_name, button_rect in self.mode_buttons.items():
            if button_rect.collidepoint(mouse_pos):
                if button_name == "back":
                    self.show_mode_selection = False
                    return None
                else:
                    self.show_mode_selection = False
                    return f"start_{button_name}"
        return None
    
    def draw_hud(self, screen, game_stats):
        
        # Painel de informações no topo
        hud_rect = pygame.Rect(0, 0, self.screen_width, 60)
        pygame.draw.rect(screen, self.DARK_GRAY, hud_rect)
        pygame.draw.rect(screen, self.WHITE, hud_rect, 2)
        
        # Estatísticas do jogo
        stats_text = [
            f"Atacantes Ativos: {game_stats.get("active_attackers", 0)}",
            f"Atacantes Eliminados: {game_stats.get("eliminated_attackers", 0)}",
            f"Atacantes que Chegaram: {game_stats.get("successful_attackers", 0)}",
            f"Torres: {game_stats.get("towers", 0)}",
            f"Pontuação: {game_stats.get("score", 0)}"
        ]
        
        x_offset = 10
        for i, stat in enumerate(stats_text):
            text_surface = self.font_small.render(stat, True, self.WHITE)
            screen.blit(text_surface, (x_offset, 10))
            x_offset += text_surface.get_width() + 20
        
        # Modo de jogo atual
        mode_text = f"Modo: {game_stats.get("player_mode", "Espectador")}"
        mode_surface = self.font_small.render(mode_text, True, self.YELLOW)
        screen.blit(mode_surface, (10, 35))
    
    def draw_pause_overlay(self, screen):
        
        # Overlay semi-transparente
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(self.BLACK)
        screen.blit(overlay, (0, 0))
        
        # Texto de pausa
        pause_text = self.font_large.render("PAUSADO", True, self.WHITE)
        pause_rect = pause_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
        screen.blit(pause_text, pause_rect)
        
        instruction_text = self.font_medium.render("Pressione ESC para continuar", True, self.LIGHT_GRAY)
        instruction_rect = instruction_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50))
        screen.blit(instruction_text, instruction_rect)
    
    def draw_game_over(self, screen, final_stats):
        
        # Overlay semi-transparente
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill(self.BLACK)
        screen.blit(overlay, (0, 0))
        
        # Título
        game_over_text = self.font_large.render("FIM DE JOGO", True, self.WHITE)
        game_over_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
        screen.blit(game_over_text, game_over_rect)
        
        # Estatísticas finais
        final_stats_text = [
            f"Atacantes Eliminados: {final_stats.get("eliminated_attackers", 0)}",
            f"Atacantes que Chegaram: {final_stats.get("successful_attackers", 0)}",
            f"Eficiência Defensiva: {final_stats.get("defense_efficiency", 0):.1f}%",
            f"Tempo de Sobrevivência Médio: {final_stats.get("avg_survival_time", 0):.1f}s",
            f"Pontuação Final: {final_stats.get("final_score", 0)}"
        ]
        
        for i, stat in enumerate(final_stats_text):
            text_surface = self.font_medium.render(stat, True, self.WHITE)
            text_rect = text_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 - 30 + i * 30))
            screen.blit(text_surface, text_rect)
        
        # Instruções
        restart_text = self.font_small.render("Pressione R para reiniciar ou ESC para voltar ao menu", True, self.GRAY)
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 120))
        screen.blit(restart_text, restart_rect)
    
    def draw_tower_placement_indicator(self, screen, mouse_pos, tower_type_info, cell_size, map_width, map_height):
        
        grid_x, grid_y = mouse_pos[0] // cell_size, (mouse_pos[1] - 60) // cell_size
        
        # Ajustar para o offset do mapa
        adjusted_mouse_x = mouse_pos[0]
        adjusted_mouse_y = mouse_pos[1] - 60

        if 0 <= grid_x < map_width and 0 <= grid_y < map_height:
            # Posição central da célula
            pixel_x = grid_x * cell_size + cell_size // 2
            pixel_y = grid_y * cell_size + cell_size // 2
            
            # Desenhar o quadrado da torre
            size = 18 # Tamanho da torre
            rect = pygame.Rect(
                int(pixel_x - size // 2),
                int(pixel_y - size // 2 + 60), # Adicionar offset do HUD
                size,
                size
            )
            pygame.draw.rect(screen, tower_type_info["color"], rect)
            pygame.draw.rect(screen, self.WHITE, rect, 2)
            
            # Desenhar símbolo do tipo
            font = pygame.font.Font(None, 16)
            symbol = tower_type_info["name"][0]
            text = font.render(symbol, True, self.WHITE)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

            # Desenhar o alcance da torre
            range_radius = tower_type_info["range"] * cell_size
            pygame.draw.circle(screen, (255, 255, 255, 50), (int(pixel_x), int(pixel_y + 60)), range_radius, 1)
            
            # Desenhar um círculo semi-transparente para o alcance
            range_surface = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (255, 255, 255, 50), (range_radius, range_radius), range_radius)
            screen.blit(range_surface, (int(pixel_x - range_radius), int(pixel_y + 60 - range_radius)))




