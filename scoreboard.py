import pygame, sys

# --- GPIO SETUP (cross-platform safe) ---
try:
    from gpiozero import Button
    button = Button(17)  # GPIO 17 on Raspberry Pi (physical pin 11)
    print("✅ GPIO detected: running on Raspberry Pi hardware.")
except Exception as e:
    print(f"⚠️ GPIO not available ({e}). Using mock button for testing.")
    class MockButton:
        @property
        def is_pressed(self): return False
        def close(self): pass
    button = MockButton()

# --- INITIALIZE PYGAME ---
pygame.init()
WIDTH, HEIGHT = 1000, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHU PIONEER ARENA")

# --- LOAD IMAGES ---
rink_img = pygame.image.load("assets/icerink.png").convert()
jumbo_img = pygame.image.load("assets/jumboT.png").convert_alpha()

# Scale images
rink_img = pygame.transform.scale(rink_img, (WIDTH, HEIGHT))
jumbo_img = pygame.transform.scale(jumbo_img, (800, 600))

# Position jumbotron
jumbo_x = WIDTH // 2 - jumbo_img.get_width() // 2
jumbo_y = 50

# Cutout region (centered inside jumbo)
cutout_width, cutout_height = 460, 140
cutout_x = jumbo_x + (jumbo_img.get_width() - cutout_width) // 2
cutout_y = jumbo_y + 60
cutout_rect = pygame.Rect(cutout_x, cutout_y, cutout_width, cutout_height)

# --- FONTS ---
small_font = pygame.font.SysFont("Courier New", 28, bold=True)
medium_font = pygame.font.SysFont("Courier New", 48, bold=True)

# --- GAME STATE ---
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

    # --- Score (centered inside cutout) ---
    score_text = str(score)
    font = pygame.font.SysFont("Courier New", 48, bold=True)
    base = font.render(score_text, True, (255, 255, 255))
    base = pygame.transform.scale(base, (base.get_width() * 3, base.get_height() * 3))  # scale=3
    mask = pygame.mask.from_surface(base)
    text_width = mask.get_size()[0]

    draw_dot_text(
        SCREEN, score_text,
        cutout_rect.centerx - text_width // 2,
        cutout_rect.y + 200,  # adjust for vertical placement
        (255, 255, 255), scale=3
    )

    # --- Pioneer letters ---
    draw_pioneer(
        SCREEN,
        cutout_rect.x,
        cutout_rect.y + cutout_rect.height + 258,
        collected
    )

    # --- Balls left ---
    balls_surf = small_font.render(f"Balls: {balls_left}", True, (255, 255, 255))
    SCREEN.blit(balls_surf, (40, HEIGHT - 60))

    # --- Jackpot message ---
    if mega_jackpot:
        mj = medium_font.render("MEGA JACKPOT!!", True, (206, 17, 65))
        SCREEN.blit(mj, (WIDTH // 2 - mj.get_width() // 2, HEIGHT - 80))

    # --- Debug overlay ---
    if debug_mode:
        pygame.draw.rect(SCREEN, (255, 0, 0), cutout_rect, 2)
        step_x = cutout_rect.width // 10
        step_y = cutout_rect.height // 5
        for gx in range(cutout_rect.x, cutout_rect.right, step_x):
            pygame.draw.line(SCREEN, (255, 0, 0), (gx, cutout_rect.y), (gx, cutout_rect.bottom), 1)
        for gy in range(cutout_rect.y, cutout_rect.bottom, step_y):
            pygame.draw.line(SCREEN, (255, 0, 0), (cutout_rect.x, gy), (cutout_rect.right, gy), 1)

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
                score, balls_left, collected, mega_jackpot = 0, 2, 0, False
            elif e.key == pygame.K_d:
                debug_mode = not debug_mode

    # --- Physical switch on Raspberry Pi ---
    if button.is_pressed:
        score += 1000
        pygame.time.wait(200)  # debounce delay

    # --- Simulated button for PC testing (ENTER key) ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
        score += 1000
        pygame.time.wait(200)

    draw_layout()
    pygame.display.flip()
    clock.tick(60)

# --- CLEAN EXIT ---
button.close()
pygame.quit()
sys.exit()
