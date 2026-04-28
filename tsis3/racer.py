import pygame
import random
import os

WIDTH, HEIGHT = 400, 600

# Sprite Groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()
powerups = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

class Player(pygame.sprite.Sprite):
    def __init__(self, image_path):
        super().__init__()
        self.original_image = pygame.image.load(image_path)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 70)
        self.speed = 5
        self.shielded = False
        
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.move_ip(-self.speed, 0)
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.move_ip(self.speed, 0)

class Traffic(pygame.sprite.Sprite):
    def __init__(self, image_path, speed):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.speed = speed
        self.reset()

    def reset(self):
        self.rect.top = -100
        # Lane logic (3 lanes)
        lane = random.randint(0, 2)
        self.rect.centerx = [65, 200, 335][lane]
        # Check for overlap with other sprites in reset
        if pygame.sprite.spritecollideany(self, all_sprites):
            self.reset()

    def move(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > HEIGHT:
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type, color, width=40, height=40):
        super().__init__()
        self.type = type # 'oil', 'pothole', 'barrier'
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        if type == 'oil':
            pygame.draw.ellipse(self.image, (50, 50, 50), (0, 0, width, height))
        elif type == 'pothole':
            pygame.draw.ellipse(self.image, (100, 70, 0), (0, 0, width, height))
        elif type == 'barrier':
            pygame.draw.rect(self.image, (200, 0, 0), (0, 10, width, 20))
        
        self.rect = self.image.get_rect()
        self.rect.top = -50
        self.rect.centerx = random.choice([65, 200, 335])
        
    def move(self, road_speed):
        self.rect.move_ip(0, road_speed)
        if self.rect.top > HEIGHT:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, image, weight):
        super().__init__()
        self.weight = weight
        size = 25 + weight * 5
        self.image = pygame.transform.scale(image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.top = -50
        self.rect.centerx = random.randint(30, WIDTH - 30)

    def move(self, road_speed):
        self.rect.move_ip(0, road_speed)
        if self.rect.top > HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, type, color):
        super().__init__()
        self.type = type # 'nitro', 'shield', 'repair'
        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        pygame.draw.rect(self.image, (255, 255, 255), (0,0,30,30), 2)
        self.rect = self.image.get_rect()
        self.rect.top = -50
        self.rect.centerx = random.randint(30, WIDTH - 30)
        self.spawn_time = pygame.time.get_ticks()

    def move(self, road_speed):
        self.rect.move_ip(0, road_speed)
        if self.rect.top > HEIGHT or pygame.time.get_ticks() - self.spawn_time > 10000:
            self.kill()
