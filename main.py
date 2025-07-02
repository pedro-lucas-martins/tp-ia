import pygame
import sys
from enum import Enum
from game import Game
from ui import UI

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSED = 4

class Main:
    def __init__(self):
        # Configurar Pygame para não usar áudio (evitar erros ALSA)
        import os
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        
        # Inicialização do Pygame
        pygame.init()
        
        # Configurações da tela
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Jogo de Segurança Cibernética - Tower Defense")
        
        # Clock para controlar FPS
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # Estado do jogo
        self.game_state = GameState.MENU
        self.running = True
        # Instâncias dos módulos principais
        self.ui = UI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.game = Game(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.ui)
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == GameState.PLAYING:
                        self.game_state = GameState.PAUSED
                    elif self.game_state == GameState.PAUSED:
                        self.game_state = GameState.PLAYING
                    elif self.game_state == GameState.MENU:
                        self.running = False
                
                elif event.key == pygame.K_SPACE:
                    if self.game_state == GameState.MENU:
                        self.game_state = GameState.PLAYING
                        self.game.start_new_game()
                
                elif event.key == pygame.K_r:
                    if self.game_state == GameState.GAME_OVER:
                        self.game_state = GameState.PLAYING
                        self.game.start_new_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == GameState.MENU:
                    # Processar cliques no menu
                    menu_action = self.ui.handle_menu_click(event.pos)
                    if menu_action and menu_action.startswith("start_"):
                        # Extrair modo do jogador
                        mode_name = menu_action.replace("start_", "")
                        if mode_name == "spectator":
                            from game import PlayerMode
                            self.game.set_player_mode(PlayerMode.SPECTATOR)
                        elif mode_name == "attacker":
                            from game import PlayerMode
                            self.game.set_player_mode(PlayerMode.ATTACKER)
                        elif mode_name == "defender":
                            from game import PlayerMode
                            self.game.set_player_mode(PlayerMode.DEFENDER)
                        
                        self.game_state = GameState.PLAYING
                        self.game.start_new_game()
                    elif menu_action == "quit":
                        self.running = False
                
                elif self.game_state == GameState.PLAYING:
                    # Passar eventos de mouse para o jogo
                    self.game.handle_mouse_click(event.pos, event.button)
    
    def update(self):
        
        if self.game_state == GameState.PLAYING:
            game_result = self.game.update()
            if game_result == "game_over":
                self.game_state = GameState.GAME_OVER
    
    def render(self):
        
        # Limpar a tela
        self.screen.fill((0, 0, 0))  # Preto
        
        if self.game_state == GameState.MENU:
            self.ui.draw_menu(self.screen)
        
        elif self.game_state == GameState.PLAYING:
            self.game.render(self.screen)
            self.ui.draw_hud(self.screen, self.game.get_game_stats())
        
        elif self.game_state == GameState.PAUSED:
            self.game.render(self.screen)
            self.ui.draw_pause_overlay(self.screen)
        
        elif self.game_state == GameState.GAME_OVER:
            self.game.render(self.screen)
            self.ui.draw_game_over(self.screen, self.game.get_final_stats())
        
        # Atualizar a tela
        pygame.display.flip()
    
    def run(self):
        
        print("Iniciando Jogo")
        print("Pressione ESPAÇO para começar ou ESC para sair")
        
        while self.running:
            # Processar eventos
            self.handle_events()
            
            # Atualizar lógica
            self.update()
            
            # Renderizar
            self.render()
            
            # Controlar FPS
            self.clock.tick(self.FPS)
        
        # Finalizar Pygame
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Main()
    game.run()

