import pygame
import random
import time

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialize Pygame
pygame.init()

# Game dimensions
WIDTH = 600
HEIGHT = 600
CELL = 30

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - Lab 11")

# Fonts
font = pygame.font.SysFont(None, 36)
image_game_over = font.render("Game Over", True, RED)
image_game_over_rect = image_game_over.get_rect(center = (WIDTH // 2, HEIGHT // 2))
sc_rect = image_game_over.get_rect(center = (WIDTH // 2, HEIGHT // 2 + 30))

def draw_grid():
    """Draws a grid on the screen."""
    for i in range(HEIGHT // CELL):
        for j in range(WIDTH // CELL):
            if j != 0:
                pygame.draw.rect(screen, GRAY, (i * CELL, j * CELL, CELL, CELL), 1)

class Point:
    """Represents a coordinate on the grid."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Snake:
    """Snake class handling movement, growth, and collision."""
    def __init__(self):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]   
        self.dx = 1
        self.dy = 0
        self.score = 0
        self.level = 1
        self.alive = True

    def move(self):
        # Move body segments
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        # Move head
        self.body[0].x += self.dx
        self.body[0].y += self.dy

        # Boundary checks
        if self.body[0].x > WIDTH // CELL - 1 or self.body[0].x < 0 or \
           self.body[0].y > HEIGHT // CELL - 1 or self.body[0].y <= 0:
            self.alive = False

        # Self-collision check
        head = self.body[0]
        for segment in self.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                self.alive = False
                break

    def draw(self):
        # Draw head and body segments
        head = self.body[0]
        pygame.draw.rect(screen, RED, (head.x * CELL, head.y * CELL, CELL, CELL))
        for segment in self.body[1:]:
            pygame.draw.rect(screen, YELLOW, (segment.x * CELL, segment.y * CELL, CELL, CELL))

    def check_collision(self, food):
        # Check collision with food
        head = self.body[0]
        if head.x == food.pos.x and head.y == food.pos.y:
            self.score += food.weight # Add food's weight to score
            self.body.append(Point(head.x, head.y)) # Grow snake
            food.generate_random_pos(self.body) # Regenerate food
            self.level = 1 + self.score // 3 # Level up every 3 score points

class Food:
    """Food class with weights and a disappearance timer."""
    def __init__(self):
        self.pos = Point(9, 9)
        self.weight = 1
        self.timer = 0
        self.lifetime = 5000 # Lifetime in milliseconds

    def draw(self):
        # Change color based on weight
        color = GREEN
        if self.weight == 2: color = BLUE
        if self.weight == 3: color = RED
        pygame.draw.rect(screen, color, (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))

    def generate_random_pos(self, snake_body):
        """Generates a new random position and weight for the food."""
        while True:
            self.pos.x = random.randint(0, WIDTH // CELL - 1)       
            self.pos.y = random.randint(0, HEIGHT // CELL - 1)      
            if not any(self.pos.x == s.x and self.pos.y == s.y for s in snake_body) and self.pos.y > 0:
                break
        self.weight = random.randint(1, 3) # Random weight between 1 and 3
        self.timer = pygame.time.get_ticks() # Record time of generation
        self.lifetime = random.randint(3000, 7000) # Random lifetime 3-7 seconds

    def is_expired(self):
        """Checks if the food has exceeded its lifetime."""
        return pygame.time.get_ticks() - self.timer > self.lifetime

# Game setup
FPS = 5
clock = pygame.time.Clock()
food = Food()
snake = Snake()
food.generate_random_pos(snake.body)
running = True

while running:
    # Game Over screen
    if not snake.alive:
        screen.fill(BLACK)
        screen.blit(image_game_over, image_game_over_rect)
        stra = f"Score: {snake.score} Level: {snake.level}"
        sc_r = font.render(stra, True, WHITE)
        screen.blit(sc_r, sc_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
        continue

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and snake.dx != -1:      
                snake.dx, snake.dy = 1, 0
            elif event.key == pygame.K_LEFT and snake.dx != 1:      
                snake.dx, snake.dy = -1, 0
            elif event.key == pygame.K_DOWN and snake.dy != -1:     
                snake.dx, snake.dy = 0, 1
            elif event.key == pygame.K_UP and snake.dy != 1:        
                snake.dx, snake.dy = 0, -1

    # Logic
    if food.is_expired():
        food.generate_random_pos(snake.body)

    snake.move()
    snake.check_collision(food)

    # Rendering
    screen.fill(BLACK)
    draw_grid()
    snake.draw()
    food.draw()
    
    # UI Text
    sc_text = font.render(f'Score: {snake.score}', True, WHITE)
    lv_text = font.render(f'Level: {snake.level}', True, WHITE)
    screen.blit(sc_text, (5, 5))
    screen.blit(lv_text, (WIDTH - 120, 5))

    pygame.display.flip()
    clock.tick(FPS + snake.level)

pygame.quit()
