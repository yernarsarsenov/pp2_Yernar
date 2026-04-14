import pygame
import sys
import os
from player import MusicPlayer

WIDTH, HEIGHT = 600, 450 # Increased height slightly for the menu
BG_COLOR = (28, 28, 28)
TEXT_COLOR = (0, 255, 127) # A nice "Kanye neon green"

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey's Music Player")
    
    # Setup Player
    music_dir = os.path.join(os.path.dirname(__file__), "music")
    player = MusicPlayer(music_dir)
    
    # Fonts
    font = pygame.font.SysFont("Arial", 22)
    big_font = pygame.font.SysFont("Arial", 30, bold=True)

    while True:
        screen.fill(BG_COLOR)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:     # Play/Pause
                    player.play_toggle()
                elif event.key == pygame.K_n:   # Next
                    player.next_track()
                elif event.key == pygame.K_b:   # Back (Previous)
                    player.prev_track()
                elif event.key == pygame.K_s:   # Stop (Reset)
                    player.stop()
                elif event.key == pygame.K_q:   # Quit
                    pygame.quit(); sys.exit()

        # --- 1. DISPLAY CURRENT STATUS ---
        track_name = player.get_current_track_name()
        status_text = "PAUSED" if player.is_paused else "PLAYING"
        if not player.started: status_text = "READY"
        
        display_str = f"{status_text}: {track_name}"
        status_surf = big_font.render(display_str, True, TEXT_COLOR)
        screen.blit(status_surf, (WIDTH//2 - status_surf.get_width()//2, 100))

        # --- 2. THE MENU (The Part You Asked For) ---
        # Draw a line to separate music info from controls
        pygame.draw.line(screen, (70, 70, 70), (50, 200), (WIDTH-50, 200), 2)
        
        menu_items = [
            "P - Play / Pause (Resume)",
            "S - Stop (Reset to start)",
            "N - Next Track",
            "B - Previous Track",
            "Q - Quit Player"
        ]

        # Loop through the list to draw each menu line
        for i, item in enumerate(menu_items):
            menu_surf = font.render(item, True, (180, 180, 180))
            screen.blit(menu_surf, (80, 230 + (i * 35)))

        pygame.display.flip()

if __name__ == "__main__":
    main()