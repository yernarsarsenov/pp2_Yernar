import pygame
import random
import os
import time
from racer import Player, Traffic, Coin, PowerUp, Obstacle, all_sprites, enemies, coins, powerups, obstacles
from persistence import get_leaderboard, save_score, get_settings, save_settings
from ui import Button, draw_text, get_username

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer Pro - TSIS 3")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Assets
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")

def get_asset(filename):
    return os.path.join(ASSETS_PATH, filename)

# Load Images
bg_img = pygame.image.load(get_asset("road.png"))
coin_img = pygame.image.load(get_asset("coin.png"))
crash_sound = pygame.mixer.Sound(get_asset("crash.wav"))
pygame.mixer.music.load(get_asset("background.wav"))

# Fonts
font_huge = pygame.font.SysFont("Verdana", 50)
font_large = pygame.font.SysFont("Verdana", 30)
font_med = pygame.font.SysFont("Verdana", 20)
font_small = pygame.font.SysFont("Verdana", 15)

def settings_screen():
    settings = get_settings()
    running = True
    while running:
        screen.fill(WHITE)
        draw_text(screen, "Settings", font_large, BLACK, (WIDTH//2, 50))
        
        sound_text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        difficulty_text = f"Difficulty: {settings['difficulty']}"
        color_text = f"Car Color: {settings['car_color']}"
        
        btn_sound = Button(100, 150, 200, 50, sound_text, font_med)
        btn_diff = Button(100, 250, 200, 50, difficulty_text, font_med)
        btn_color = Button(100, 350, 200, 50, color_text, font_med)
        btn_back = Button(100, 500, 200, 50, "Back", font_med)
        
        for btn in [btn_sound, btn_diff, btn_color, btn_back]:
            btn.draw(screen)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if btn_sound.is_clicked(event):
                settings['sound'] = not settings['sound']
                if not settings['sound']: pygame.mixer.music.stop()
            if btn_diff.is_clicked(event):
                diffs = ["Easy", "Medium", "Hard"]
                settings['difficulty'] = diffs[(diffs.index(settings['difficulty']) + 1) % 3]
            if btn_color.is_clicked(event):
                colors = ["Red", "Blue", "Green"]
                settings['car_color'] = colors[(colors.index(settings['car_color']) + 1) % 3]
            if btn_back.is_clicked(event):
                save_settings(settings)
                return
        
        pygame.display.flip()

def leaderboard_screen():
    running = True
    while running:
        screen.fill(WHITE)
        draw_text(screen, "Leaderboard", font_large, BLACK, (WIDTH//2, 50))
        
        lb = get_leaderboard()
        for i, entry in enumerate(lb):
            txt = f"{i+1}. {entry['name']} - {entry['score']} pts"
            draw_text(screen, txt, font_med, BLACK, (WIDTH//2, 120 + i*35))
            
        btn_back = Button(100, 520, 200, 50, "Back", font_med)
        btn_back.draw(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if btn_back.is_clicked(event): return
            
        pygame.display.flip()

def game_over_screen(name, score, distance, coins_count):
    save_score(name, score, distance)
    running = True
    while running:
        screen.fill(RED)
        draw_text(screen, "GAME OVER", font_huge, WHITE, (WIDTH//2, 100))
        draw_text(screen, f"Score: {score}", font_large, BLACK, (WIDTH//2, 200))
        draw_text(screen, f"Distance: {round(distance, 1)}m", font_med, BLACK, (WIDTH//2, 250))
        draw_text(screen, f"Coins: {coins_count}", font_med, BLACK, (WIDTH//2, 290))
        
        btn_retry = Button(100, 400, 200, 50, "Retry", font_med)
        btn_menu = Button(100, 470, 200, 50, "Main Menu", font_med)
        
        for btn in [btn_retry, btn_menu]: btn.draw(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if btn_retry.is_clicked(event): return True
            if btn_menu.is_clicked(event): return "menu"
            
        pygame.display.flip()

def play_game(username):
    # Reset groups
    for group in [all_sprites, enemies, coins, powerups, obstacles]:
        group.empty()
        
    settings = get_settings()
    player = Player(get_asset("Player.png")) # Add car color logic later if needed
    all_sprites.add(player)
    
    collected_coins = 0
    score = 0
    distance = 0
    road_speed = 5
    if settings['difficulty'] == "Easy": road_speed = 4
    if settings['difficulty'] == "Hard": road_speed = 7
    
    active_powerup = None
    powerup_timer = 0
    
    if settings['sound']: pygame.mixer.music.play(-1)
    
    clock = pygame.time.Clock()
    running = True
    last_enemy_spawn = 0
    last_coin_spawn = 0
    
    while running:
        now = pygame.time.get_ticks()
        
        # Difficulty scaling
        current_road_speed = road_speed + (distance // 500)
        
        # Spawning logic
        if now - last_enemy_spawn > max(500, 2000 - (distance // 10)):
            e = Traffic(get_asset("Enemy.png"), current_road_speed + 2)
            enemies.add(e)
            all_sprites.add(e)
            last_enemy_spawn = now
            
        if now - last_coin_spawn > 1500:
            c = Coin(coin_img, random.randint(1, 3))
            coins.add(c)
            all_sprites.add(c)
            last_coin_spawn = now
            
        if random.random() < 0.005:
            o_type = random.choice(['oil', 'pothole', 'barrier'])
            o = Obstacle(o_type, BLACK)
            obstacles.add(o)
            all_sprites.add(o)
            
        if random.random() < 0.002:
            p_type = random.choice(['nitro', 'shield', 'repair'])
            p_color = BLUE if p_type == 'nitro' else (GREEN if p_type == 'repair' else YELLOW)
            p = PowerUp(p_type, p_color)
            powerups.add(p)
            all_sprites.add(p)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False

        player.move()
        for e in enemies: e.move()
        for c in coins: c.move(current_road_speed)
        for p in powerups: p.move(current_road_speed)
        for o in obstacles: o.move(current_road_speed)
        
        distance += current_road_speed * 0.1
        score = int(distance + collected_coins * 10)

        # Powerup Logic
        if active_powerup == 'nitro':
            if pygame.time.get_ticks() > powerup_timer:
                active_powerup = None
                road_speed -= 3
        
        # Collisions
        c_hit = pygame.sprite.spritecollide(player, coins, True)
        for c in c_hit:
            collected_coins += c.weight
            
        p_hit = pygame.sprite.spritecollide(player, powerups, True)
        for p in p_hit:
            active_powerup = p.type
            if p.type == 'nitro':
                road_speed += 3
                powerup_timer = pygame.time.get_ticks() + 5000
            elif p.type == 'shield':
                player.shielded = True
                powerup_timer = 0 # stays until hit
            elif p.type == 'repair':
                # repair logic: could clear obstacles or restore HP if we had it
                for o in obstacles: o.kill()
                active_powerup = None

        if pygame.sprite.spritecollideany(player, enemies) or pygame.sprite.spritecollideany(player, obstacles):
            if player.shielded:
                player.shielded = False
                active_powerup = None
                # Kill the thing we hit
                hit_enemy = pygame.sprite.spritecollideany(player, enemies)
                if hit_enemy: hit_enemy.kill()
                hit_obs = pygame.sprite.spritecollideany(player, obstacles)
                if hit_obs: hit_obs.kill()
            else:
                if settings['sound']:
                    pygame.mixer.music.stop()
                    crash_sound.play()
                res = game_over_screen(username, score, distance, collected_coins)
                return res

        # Draw
        screen.blit(bg_img, (0, 0))
        for sprite in all_sprites:
            screen.blit(sprite.image, sprite.rect)
            
        # UI Overlay
        draw_text(screen, f"Score: {score}", font_med, BLACK, (70, 30))
        draw_text(screen, f"Distance: {int(distance)}m", font_small, BLACK, (70, 60))
        draw_text(screen, f"Coins: {collected_coins}", font_small, BLACK, (70, 80))
        
        if active_powerup:
            color = BLUE if active_powerup == 'nitro' else YELLOW
            draw_text(screen, f"ACTIVE: {active_powerup.upper()}", font_med, color, (WIDTH//2, 30))

        pygame.display.flip()
        clock.tick(60)

def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text(screen, "RACER PRO", font_huge, BLACK, (WIDTH//2, 100))
        
        btn_play = Button(100, 200, 200, 50, "Play", font_med)
        btn_lb = Button(100, 270, 200, 50, "Leaderboard", font_med)
        btn_settings = Button(100, 340, 200, 50, "Settings", font_med)
        btn_quit = Button(100, 410, 200, 50, "Quit", font_med)
        
        for btn in [btn_play, btn_lb, btn_settings, btn_quit]:
            btn.draw(screen)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if btn_play.is_clicked(event):
                name = get_username(screen, font_large)
                if name:
                    res = play_game(name)
                    while res == True:
                        res = play_game(name)
            if btn_lb.is_clicked(event):
                leaderboard_screen()
            if btn_settings.is_clicked(event):
                settings_screen()
            if btn_quit.is_clicked(event):
                return
                
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
    pygame.quit()
