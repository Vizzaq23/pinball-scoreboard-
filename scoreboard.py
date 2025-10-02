import pygame, sys

pygame.init()
WIDTH, HEIGHT = 1000, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHU PIONEER ARENA")

# Load images
rink_img = pygame.image.load("assets/icerink.png").convert()
jumbo_img = pygame.image.load("assets/jumboT.png").convert_alpha()

# Scale images
rink_img = pygame.transform.scale(rink_img, (WIDTH, HEIGHT))
jumbo_img = pygame.transform.scale(jumbo_img, (800, 350))

# Position jumbotron
jumbo_x = WIDTH // 2 - jumbo_img.get_width() // 2
jumbo_y = 80

# Cutout region (centered inside jumbo)
cutout_width, cutout_height = 460, 140
cutout_x = jumbo_x + (jumbo_img.get_width() - cutout_width) // 2
cutout_y = jumbo_y + 60
cutout_rect = pygame.Rect(cutout_x, cutout_y, cutout_width, cutout_height)

# Fonts
small_font = pygame.font.SysFont("Courier New", 28, bold=True)
medium_font = pygame.font.SysFont("Courier New", 48, bold=True)

# Game state
score = 0
balls_left = 2
collected = 0
mega_jackpot = False
debug_mode = False

clock = pygame.time.Clock()

# --- DOT MATRIX RENDERER ---
def draw_dot_text(surface, text, x, y, color=(255, 255, 255), scale=2, spacing=3):
    font = pygame.font.SysFont("Courier New", 48, bold=True)
    base = font.render(text, True, (255, 255, 255))
    base = pygame.transform.scale(base, (base.get_width() * scale, base.get_height() * scale))
    mask = pygame.mask.from_surface(base)

    for px in range(mask.get_size()[0]):
        for py in range(mask.get_size()[1]):
            if mask.get_at((px, py)):
                if (px % spacing == 0) and (py % spacing == 0):
                    pygame.draw.circle(surface, color, (x + px, y + py), 2)

# --- PIONEER BULBS ---
def draw_pioneer(surface, x, y, collected):
    word = "PIONEER"
    for i, letter in enumerate(word):
        if i < collected:
            draw_dot_text(surface, letter, x + i * 70, y, (255, 215, 60), scale=2)
        else:
            draw_dot_text(surface, "•", x + i * 70, y, (120, 120, 60), scale=2)

# --- DRAW EVERYTHING ---
def draw_layout():
    SCREEN.blit(rink_img, (0, 0))                   
    SCREEN.blit(jumbo_img, (jumbo_x, jumbo_y))     

    # Score (true centering by measuring surface size)
    score_text = str(score)
    temp_font = pygame.font.SysFont("Courier New", 48, bold=True)
    temp_render = temp_font.render(score_text, True, (255, 255, 255))
    scaled_width = temp_render.get_width() * 3  # match scale=3
    draw_dot_text(
        SCREEN, score_text,
        cutout_rect.centerx - scaled_width // 2,
        cutout_rect.y + 20,
        (255, 255, 255), scale=3
    )

    # Pioneer letters
    draw_pioneer(SCREEN, cutout_rect.x + 30, cutout_rect.y + cutout_rect.height - 60, collected)

    # Balls left
    balls_surf = small_font.render(f"Balls: {balls_left}", True, (255, 255, 255))
    SCREEN.blit(balls_surf, (40, HEIGHT - 60))

    # Jackpot message
    if mega_jackpot:
        mj = medium_font.render("MEGA JACKPOT!!", True, (206, 17, 65))
        SCREEN.blit(mj, (WIDTH // 2 - mj.get_width() // 2, HEIGHT - 80))

    # Debug overlay
    if debug_mode:
        pygame.draw.rect(SCREEN, (255, 0, 0), cutout_rect, 2)
        step_x = cutout_rect.width // 10
        step_y = cutout_rect.height // 5
        for gx in range(cutout_rect.x, cutout_rect.right, step_x):
            pygame.draw.line(SCREEN, (255, 0, 0), (gx, cutout_rect.y), (gx, cutout_rect.bottom), 1)
