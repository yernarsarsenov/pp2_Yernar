import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

class Button:
    def __init__(self, x, y, width, height, text, font, color=GRAY, hover_color=(170, 170, 170)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        txt_surf = self.font.render(self.text, True, BLACK)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def draw_text(screen, text, font, color, center_pos):
    txt_surf = font.render(text, True, color)
    txt_rect = txt_surf.get_rect(center=center_pos)
    screen.blit(txt_surf, txt_rect)

def get_username(screen, font):
    username = ""
    input_active = True
    while input_active:
        screen.fill(WHITE)
        draw_text(screen, "Enter Username:", font, BLACK, (screen.get_width()//2, 200))
        draw_text(screen, username + "_", font, BLUE, (screen.get_width()//2, 300))
        draw_text(screen, "Press Enter to Start", pygame.font.SysFont("Verdana", 20), BLACK, (screen.get_width()//2, 450))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username: input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 15:
                        username += event.unicode
        pygame.display.flip()
    return username
