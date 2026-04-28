import os, random, json, sys, pygame
from game import Snake, Food, PowerUp, Obstacle, Point, WIDTH, HEIGHT, CELL
from db import DBManager

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Pro - TSIS 4")

# Fonts
font_large = pygame.font.SysFont("Verdana", 40)
font_med = pygame.font.SysFont("Verdana", 25)
font_small = pygame.font.SysFont("Verdana", 18)

db = DBManager()

class Button:
    def __init__(self, x, y, w, h, text, color=GRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        txt = font_med.render(self.text, True, BLACK)
        screen.blit(txt, txt.get_rect(center=self.rect.center))
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_text(text, font, color, pos, center=True):
    txt = font.render(text, True, color)
    rect = txt.get_rect(center=pos) if center else txt.get_rect(topleft=pos)
    screen.blit(txt, rect)

def load_settings():
    path = os.path.join(os.path.dirname(__file__), "settings.json")
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            pass
    return {"snake_color": [0, 255, 0], "grid_overlay": True, "sound": True}

def save_settings(settings):
    path = os.path.join(os.path.dirname(__file__), "settings.json")
    with open(path, "w") as f:
        json.dump(settings, f, indent=4)

def get_username():
    name = ""
    while True:
        screen.fill(WHITE)
        draw_text("Enter Username:", font_large, BLACK, (WIDTH//2, 200))
        draw_text(name + "_", font_large, BLUE, (WIDTH//2, 300))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name: return name
                elif event.key == pygame.K_BACKSPACE: name = name[:-1]
                else: 
                    if len(name) < 12: name += event.unicode
        pygame.display.flip()

def leaderboard_screen():
    while True:
        screen.fill(WHITE)
        draw_text("Leaderboard", font_large, BLACK, (WIDTH//2, 50))
        lb = db.get_leaderboard()
        for i, (name, score, level, date) in enumerate(lb):
            txt = f"{i+1}. {name}: {score} (Lvl {level})"
            draw_text(txt, font_small, BLACK, (WIDTH//2, 120 + i*35))
        
        btn_back = Button(200, 520, 200, 50, "Back")
        btn_back.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.is_clicked(event.pos): return
        pygame.display.flip()

def settings_screen():
    settings = load_settings()
    while True:
        screen.fill(WHITE)
        draw_text("Settings", font_large, BLACK, (WIDTH//2, 50))
        
        btn_grid = Button(150, 150, 300, 50, f"Grid: {'ON' if settings['grid_overlay'] else 'OFF'}")
        btn_sound = Button(150, 230, 300, 50, f"Sound: {'ON' if settings['sound'] else 'OFF'}")
        btn_color = Button(150, 310, 300, 50, "Snake Color")
        btn_back = Button(200, 500, 200, 50, "Save & Back")
        
        for b in [btn_grid, btn_sound, btn_color, btn_back]: b.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_grid.is_clicked(event.pos): settings['grid_overlay'] = not settings['grid_overlay']
                if btn_sound.is_clicked(event.pos): settings['sound'] = not settings['sound']
                if btn_color.is_clicked(event.pos):
                    settings['snake_color'] = [random.randint(0,255), random.randint(0,255), random.randint(0,255)]
                if btn_back.is_clicked(event.pos):
                    save_settings(settings)
                    return
        pygame.display.flip()

def play_game(username):
    settings = load_settings()
    snake = Snake(settings['snake_color'])
    normal_food = Food('normal')
    poison_food = Food('poison')
    powerup = None
    level = 1
    score = 0
    personal_best = db.get_personal_best(username)
    obstacles = []
    
    normal_food.generate(snake.body, obstacles)
    poison_food.generate(snake.body, obstacles)
    
    clock = pygame.time.Clock()
    running = True
    
    powerup_end_time = 0
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Power-up expiration logic
        if powerup_end_time > 0 and current_time > powerup_end_time:
            snake.speed_modifier = 1.0
            powerup_end_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.dy != 1: snake.dx, snake.dy = 0, -1
                if event.key == pygame.K_DOWN and snake.dy != -1: snake.dx, snake.dy = 0, 1
                if event.key == pygame.K_LEFT and snake.dx != 1: snake.dx, snake.dy = -1, 0
                if event.key == pygame.K_RIGHT and snake.dx != -1: snake.dx, snake.dy = 1, 0

        snake.move()
        
        # Collision Checks
        if snake.check_boundary() or snake.check_self_collision():
            running = False
        
        # Obstacle collision
        head = snake.body[0]
        if any(head == o for o in obstacles):
            if snake.shielded: snake.shielded = False
            else: running = False
            
        # Food collision
        if head == normal_food.pos:
            score += normal_food.weight
            snake.body.append(Point(head.x, head.y))
            new_level = 1 + score // 10
            if new_level > level:
                level = new_level
                obstacles = Obstacle.generate_for_level(level, snake.body)
            normal_food.generate(snake.body, obstacles)
            
        if head == poison_food.pos:
            snake.shorten(2)
            if not snake.alive: running = False
            poison_food.generate(snake.body, obstacles)
            
        # Powerup spawn
        if powerup is None and random.random() < 0.01:
            powerup = PowerUp()
            powerup.generate(snake.body, obstacles)
        
        if powerup:
            if head == powerup.pos:
                if powerup.type == 'speed': 
                    snake.speed_modifier = 1.5
                    powerup_end_time = current_time + 5000
                elif powerup.type == 'slow':
                    snake.speed_modifier = 0.5
                    powerup_end_time = current_time + 5000
                elif powerup.type == 'shield':
                    snake.shielded = True
                powerup = None
            elif powerup.is_expired():
                powerup = None

        if normal_food.is_expired(): normal_food.generate(snake.body, obstacles)
        if poison_food.is_expired(): poison_food.generate(snake.body, obstacles)

        # Drawing
        screen.fill(BLACK)
        if settings['grid_overlay']:
            for i in range(0, WIDTH, CELL): pygame.draw.line(screen, (30,30,30), (i,0), (i, HEIGHT))
            for i in range(0, HEIGHT, CELL): pygame.draw.line(screen, (30,30,30), (0,i), (WIDTH, i))
        
        # Draw Snake
        for i, s in enumerate(snake.body):
            color = snake.color if i > 0 else WHITE
            if snake.shielded: color = BLUE if i == 0 else color
            pygame.draw.rect(screen, color, (s.x*CELL, s.y*CELL, CELL-1, CELL-1))
            
        # Draw Food
        f_color = GREEN if normal_food.weight == 1 else (BLUE if normal_food.weight == 2 else RED)
        pygame.draw.rect(screen, f_color, (normal_food.pos.x*CELL, normal_food.pos.y*CELL, CELL-1, CELL-1))
        pygame.draw.rect(screen, (100, 0, 0), (poison_food.pos.x*CELL, poison_food.pos.y*CELL, CELL-1, CELL-1))
        
        if powerup:
            p_color = PURPLE
            pygame.draw.circle(screen, p_color, (powerup.pos.x*CELL + CELL//2, powerup.pos.y*CELL + CELL//2), CELL//3)

        # Draw Obstacles
        for o in obstacles:
            pygame.draw.rect(screen, GRAY, (o.x*CELL, o.y*CELL, CELL-1, CELL-1))

        # UI
        draw_text(f"Score: {score} | Level: {level}", font_small, WHITE, (10, 10), False)
        draw_text(f"PB: {max(score, personal_best)}", font_small, YELLOW, (WIDTH - 100, 10), False)
        if snake.shielded: draw_text("SHIELD ACTIVE", font_small, BLUE, (WIDTH//2, 10))

        pygame.display.flip()
        # Dynamic Speed
        base_fps = 5 + level * 2
        clock.tick(int(base_fps * snake.speed_modifier))

    db.save_score(username, score, level)
    return game_over_screen(username, score, level, personal_best)

def game_over_screen(username, score, level, pb):
    while True:
        screen.fill(BLACK)
        draw_text("GAME OVER", font_large, RED, (WIDTH//2, 100))
        draw_text(f"Score: {score} | Level: {level}", font_med, WHITE, (WIDTH//2, 200))
        draw_text(f"Personal Best: {max(score, pb)}", font_med, YELLOW, (WIDTH//2, 250))
        
        btn_retry = Button(150, 350, 300, 50, "Retry")
        btn_menu = Button(150, 420, 300, 50, "Main Menu")
        for b in [btn_retry, btn_menu]: b.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_retry.is_clicked(event.pos): return True
                if btn_menu.is_clicked(event.pos): return "menu"
        pygame.display.flip()

def main_menu():
    username = ""
    while True:
        screen.fill(WHITE)
        draw_text("SNAKE PRO", font_large, BLACK, (WIDTH//2, 100))
        
        btn_play = Button(150, 200, 300, 50, "Play")
        btn_lb = Button(150, 280, 300, 50, "Leaderboard")
        btn_settings = Button(150, 360, 300, 50, "Settings")
        btn_quit = Button(150, 440, 300, 50, "Quit")
        
        for b in [btn_play, btn_lb, btn_settings, btn_quit]: b.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_play.is_clicked(event.pos):
                    if not username: username = get_username()
                    if username:
                        res = play_game(username)
                        while res == True: res = play_game(username)
                if btn_lb.is_clicked(event.pos): leaderboard_screen()
                if btn_settings.is_clicked(event.pos): settings_screen()
                if btn_quit.is_clicked(event.pos): pygame.quit(); sys.exit()
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
