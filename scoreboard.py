import pygame, sys

pygame.init()
WIDTH, HEIGHT = 1000, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHU PIONEER ARENA")

# Load images
rink_img = pygame.image.load("icerink.png").convert()
jumbo_img = pygame.image.load("jumboT.png").convert_alpha()

# Scale to fit window if needed
rink_img = pygame.transform.scale(rink_img, (WIDTH, HEIGHT))
jumbo_img = pygame.transform.scale(jumbo_img, (700, 250))

# Position jumbotron
jumbo_x = WIDTH//2 - jumbo_img.get_width()//2
jumbo_y = 40   # adjust this down/up depending on where you want it

# Fonts
small_font  = pygame.font.SysFont("Courier New", 28, bold=True)
medium_font = pygame.font.SysFont("Courier New", 48, bold=True)

# Game state
score = 0
high_score = 0
balls_left = 2
collected = 0
mega_jackpot = False

clock = pygame.time.Clock()

# --- DOT MATRIX RENDERER (for score + bulbs) ---
def draw_dot_text(surface, text, x, y, color=(255,255,255), scale=2, spacing=3):
    font = pygame.font.SysFont("Courier New", 48, bold=True)
    base = font.render(text, True, (255,255,255))
    base = pygame.transform.scale(base, (base.get_width()*scale, base.get_height()*scale))
    mask = pygame.mask.from_surface(base)

    for px in range(mask.get_size()[0]):
        for py in range(mask.get_size()[1]):
            if mask.get_at((px, py)):
                if (px % spacing == 0) and (py % spacing == 0):
                    pygame.draw.circle(surface, color, (x+px, y+py), 2)

# --- PIONEER BULBS ---
def draw_pioneer(surface, x, y, collected):
    word = "PIONEER"
    for i, letter in enumerate(word):
        if i < collected:
            draw_dot_text(surface, letter, x + i*70, y, (255,215,60), scale=2)  # gold lit
        else:
            draw_dot_text(surface, "•", x + i*70, y, (120,120,60), scale=2)      # dim

# --- MAIN DRAW ---
def draw_layout():
    # background rink
    SCREEN.blit(rink_img, (0,0))

    # jumbotron
    SCREEN.blit(jumbo_img, (jumbo_x, jumbo_y))

    # score in jumbotron screen
    draw_dot_text(SCREEN, str(score), jumbo_x+250, jumbo_y+90, (255,255,255), scale=3)

    # PIONEER row inside jumbotron
    draw_pioneer(SCREEN, jumbo_x+150, jumbo_y+170, collected)

    # Balls left (bottom left on ice)
    balls_surf = small_font.render(f"Balls: {balls_left}", True, (255,255,255))
    SCREEN.blit(balls_surf, (40, HEIGHT-60))

    # Jackpot notice
    if mega_jackpot:
        mj = medium_font.render("MEGA JACKPOT!!", True, (206,17,65))
        SCREEN.blit(mj, (WIDTH//2 - mj.get_width()//2, HEIGHT-80))

# --- MAIN LOOP ---
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                score += 1000
            elif e.key == pygame.K_t:
                score += 450
            elif e.key == pygame.K_g:
                if collected < len("PIONEER"):
                    collected += 1
                if collected == len("PIONEER"):
                    mega_jackpot = True
                    score += 10000
            elif e.key == pygame.K_b:
                balls_left -= 1
            elif e.key == pygame.K_r:
                score = 0
                balls_left = 2
                collected = 0
                mega_jackpot = False

    draw_layout()
    pygame.display.flip()
    clock.tick(60)

pygame.quit(); sys.exit()
