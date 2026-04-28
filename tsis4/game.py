import pygame
import random

WIDTH = 600
HEIGHT = 600
CELL = 30

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Snake:
    def __init__(self, color):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0
        self.color = color
        self.shielded = False
        self.alive = True
        self.speed_modifier = 1.0

    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y
        self.body[0].x += self.dx
        self.body[0].y += self.dy

    def check_boundary(self):
        head = self.body[0]
        if head.x >= WIDTH // CELL or head.x < 0 or \
           head.y >= HEIGHT // CELL or head.y < 0:
            if self.shielded:
                self.shielded = False
                # Bounce back or just stay inside
                head.x = max(0, min(head.x, WIDTH // CELL - 1))
                head.y = max(0, min(head.y, HEIGHT // CELL - 1))
                return False
            return True
        return False

    def check_self_collision(self):
        head = self.body[0]
        for segment in self.body[1:]:
            if head == segment:
                if self.shielded:
                    self.shielded = False
                    return False
                return True
        return False

    def shorten(self, count):
        for _ in range(count):
            if len(self.body) > 1:
                self.body.pop()
            else:
                self.alive = False
                break
        if len(self.body) <= 1:
            self.alive = False

class Food:
    def __init__(self, type='normal'):
        self.pos = Point(0, 0)
        self.type = type # 'normal', 'poison'
        self.weight = 1
        self.timer = pygame.time.get_ticks()
        self.lifetime = 7000

    def generate(self, snake_body, obstacles):
        while True:
            self.pos = Point(random.randint(0, WIDTH // CELL - 1), random.randint(0, HEIGHT // CELL - 1))
            if not any(self.pos == s for s in snake_body) and not any(self.pos == o for o in obstacles):
                break
        self.timer = pygame.time.get_ticks()
        if self.type == 'normal':
            self.weight = random.randint(1, 3)
            self.lifetime = random.randint(5000, 10000)
        else: # poison
            self.weight = 0
            self.lifetime = 8000

    def is_expired(self):
        return pygame.time.get_ticks() - self.timer > self.lifetime

class PowerUp:
    def __init__(self):
        self.pos = Point(0, 0)
        self.type = random.choice(['speed', 'slow', 'shield'])
        self.timer = pygame.time.get_ticks()
        self.lifetime = 8000

    def generate(self, snake_body, obstacles):
        while True:
            self.pos = Point(random.randint(0, WIDTH // CELL - 1), random.randint(0, HEIGHT // CELL - 1))
            if not any(self.pos == s for s in snake_body) and not any(self.pos == o for o in obstacles):
                break
        self.timer = pygame.time.get_ticks()

    def is_expired(self):
        return pygame.time.get_ticks() - self.timer > self.lifetime

class Obstacle:
    @staticmethod
    def generate_for_level(level, snake_body):
        obstacles = []
        if level < 3: return []
        num_blocks = (level - 2) * 5
        for _ in range(num_blocks):
            while True:
                p = Point(random.randint(0, WIDTH // CELL - 1), random.randint(0, HEIGHT // CELL - 1))
                # Don't place on snake or too close to head
                dist = abs(p.x - snake_body[0].x) + abs(p.y - snake_body[0].y)
                if not any(p == s for s in snake_body) and dist > 3:
                    obstacles.append(p)
                    break
        return obstacles
