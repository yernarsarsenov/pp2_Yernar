import pygame
import sys
from ball import Ball

WIDTH, HEIGHT = 800, 600
FPS = 60 # High FPS ensures smooth movement

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Smooth Diagonal Movement")
    clock = pygame.time.Clock()

    my_ball = Ball(WIDTH, HEIGHT)

    while True:
        # 1. Event Handling (Only for quitting)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # 2. Continuous Input Handling
        # This gets the state of all keyboard buttons
        keys = pygame.key.get_pressed()
        my_ball.update(keys)

        # 3. Drawing
        screen.fill((255, 255, 255))
        my_ball.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()