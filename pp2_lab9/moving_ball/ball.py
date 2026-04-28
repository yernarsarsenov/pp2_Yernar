import pygame

class Ball:
    def __init__(self, screen_width, screen_height):
        self.radius = 25
        self.color = (255, 0, 0)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width // 2
        self.y = screen_height // 2
        # Reduced step size for smoother continuous movement
        self.step = 5 

    def update(self, keys):
        """Handles multiple key presses for diagonal movement."""
        # Vertical Movement
        if keys[pygame.K_UP]:
            if self.y - self.radius - self.step >= 0:
                self.y -= self.step
        if keys[pygame.K_DOWN]:
            if self.y + self.radius + self.step <= self.screen_height:
                self.y += self.step
        
        # Horizontal Movement
        if keys[pygame.K_LEFT]:
            if self.x - self.radius - self.step >= 0:
                self.x -= self.step
        if keys[pygame.K_RIGHT]:
            if self.x + self.radius + self.step <= self.screen_width:
                self.x += self.step

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)