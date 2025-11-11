import pygame, sys, time, threading

# --- GPIO SETUP (cross-platform safe) ---
try:
    from gpiozero import Button, DigitalOutputDevice
    print("✅ GPIO detected: running on Raspberry Pi hardware.")

    # Strike plates (wired in parallel → GPIO17 → GND)
    targets_any = Button(17, pull_up=True, bounce_time=0.15)

    # Bumpers: inputs + solenoid driver outputs
    BUMPER1_PIN = 22      # input switch for bumper 1
    BUMPER2_PIN = 23      # input switch for bumper 2
    BUMPER1_GATE = 5      # MOSFET gate to bumper 1 coil
    BUMPER2_GATE = 6      # MOSFET gate to bumper 2 coil

    bumper1 = Button(BUMPER1_PIN, pull_up=True, bounce_time=0.1)
    bumper2 = Button(BUMPER2_PIN, pull_up=True, bounce_time=0.1)
    gate1 = DigitalOutputDevice(BUMPER1_GATE, active_high=True, initial_value=False)
    gate2 = DigitalOutputDevice(BUMPER2_GATE, active_high=True, initial_value=False)

    USE_GPIO = True

except Exception as e:
    print(f"⚠️ GPIO not available ({e}). Using mock mode for testing.")
    USE_GPIO = False

    class MockButton:
        @property
        def is_pressed(self): return False
        def close(self): pass

    class MockGate:
        def on(self): pass
        def off(self): pass
        def close(self): pass

    targets_any = MockButton()
    bumper1 = MockButton()
    bumper2 = MockButton()
    gate1 = MockGate()
    gate2 = MockGate()

# --- INITIALIZE PYGAME ---
pygame.init()
WIDTH, HEIGHT = 1000, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHU PIONEER ARENA")

# --- SOUND SETUP ---
pygame.mixer.init()
try:
    hit_sound = pygame.mixer.Sound("assets/hit.wav")
    bumper_sound = pygame.mixer.Sound("assets/bumper.wav")
    jackpot_sound = pygame.mixer.Sound("assets/jackpot.wav")
except Exception as e:
    print("⚠️ Sound files missing or mixer error:", e)
    hit_sound = bumper_sound = jackpot_sound = None

def play_sound(name):
    """Play a sound effect by name."""
    if name == "hit" and hit_sound: hit_sound.play()
    elif name == "bumper" and bumper_sound: bumper_sound.play()
    elif name == "jackpot" and jackpot_sound: jackpot_sound.play()

# --- BACKGROUND MUSIC SETUP ---
def start_music():
    """Start looping hockey-themed background music."""
    try:
        pygame.mixer.music.load("assets/hockey_theme.mp3")
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)  # -1 = infinite loop
        print("🎵 Background hockey music playing.")
    except Exception as e:
        print("⚠️ Could not load background music:", e)

music_on = True  # for mute toggle

# --- LOAD IMAGES ---
rink_img = pygame.image.load("assets/icerink.png").convert()
jumbo_img = pygame.image.load("assets/jumboT.png").convert_alpha()
rink_img = pygame.transform.scale(rink_img, (WIDTH, HEIGHT))
jumbo_img = pygame.transform.scale(jumbo_img, (800, 600))

jumbo_x = WIDTH // 2 - jumbo_img.get_width() // 2
jumbo_y = 50
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
def draw_dot_text(surface, text, x, y, color=(255,255,255), scale=2, spacing=3):
    font = pygame.font.SysFont("Courier New", 48, bold=True)
    base = font.render(text, True, (255,255,255))
    base = pygame.transform.scale(base, (base.get_width()*scale, base.get_height()*scale))
    mask = pygame.mask.from_surface(base)
    for px in range(mask.get_size()[0]):
        for py in range(mask.get_size()[1]):
            if mask.get_at((px, py)) and (px % spacing == 0) and (py % spacing == 0):
                pygame.draw.circle(surface, color, (x + px, y + py), 2)

# --- PIONEER BULBS ---
def draw_pioneer(surface, x, y, collected):
    word = "PIONEER"
    for i, letter in enumerate(word):
        if i < collected:
            draw_dot_text(surface, letter, x + i * 70, y, (255,215,60), scale=2)
        else:
            draw_dot_text(surface, "•", x + i * 70, y, (120,120,60), scale=2)

# --- DRAW EVERYTHING ---
def draw_layout():
    SCREEN.blit(rink_img, (0, 0))
    SCREEN.blit(jumbo_img, (jumbo_x, jumbo_y))
    # Score
    score_text = str(score)
    font = pygame.font.SysFont("Courier New", 48, bold=True)
    base = font.render(score_text, True, (255,255,255))
    base = pygame.transform.scale(base, (base.get_width()*3, base.get_height()*3))
    mask = pygame.mask.from_surface(base)
    text_width = mask.get_size()[0]
    draw_dot_text(SCREEN, score_text,
                  cutout_rect.centerx - text_width // 2,
                  cutout_rect.y + 200,
                  (255,255,255), scale=3)
    # Pioneer letters
    draw_pioneer(SCREEN,
                 cutout_rect.x,
                 cutout_rect.y + cutout_rect.height + 258,
                 collected)
    # Balls left
    SCREEN.blit(small_font.render(f"Balls: {balls_left}", True, (255,255,255)),
                (40, HEIGHT - 60))
    # Jackpot
    if mega_jackpot:
        mj = medium_font.render("MEGA JACKPOT!!", True, (206,17,65))
        SCREEN.blit(mj, (WIDTH // 2 - mj.get_width() // 2, HEIGHT - 80))
    # Debug overlay
    if debug_mode:
        pygame.draw.rect(SCREEN, (255,0,0), cutout_rect, 2)
        step_x = cutout_rect.width // 10
        step_y = cutout_rect.height // 5
        for gx in range(cutout_rect.x, cutout_rect.right, step_x):
            pygame.draw.line(SCREEN, (255,0,0), (gx, cutout_rect.y), (gx, cutout_rect.bottom), 1)
        for gy in range(cutout_rect.y, cutout_rect.bottom, step_y):
            pygame.draw.line(SCREEN, (255,0,0), (cutout_rect.x, gy), (cutout_rect.right, gy), 1)

# --- STRIKE PLATE HANDLER ---
last_hit = 0
HIT_COOLDOWN = 0.4  # seconds

def on_target_hit():
    global last_hit, score
    now = time.time()
    if now - last_hit >= HIT_COOLDOWN:
        score += 500
        last_hit = now
        print("🎯 Target hit! +500")
        play_sound("hit")

# --- BUMPER HANDLERS ---
last_bumper_hit = {1: 0, 2: 0}
BUMPER_COOLDOWN = 0.3
PULSE_TIME = 0.1

def on_bumper_hit(bumper_id):
    global last_bumper_hit, score
    now = time.time()
    if now - last_bumper_hit[bumper_id] >= BUMPER_COOLDOWN:
        score += 100
        last_bumper_hit[bumper_id] = now
        print(f" Bumper {bumper_id} hit! +100")
        play_sound("bumper")
        gate = gate1 if bumper_id == 1 else gate2
        threading.Thread(target=pulse_solenoid, args=(gate,), daemon=True).start()

def pulse_solenoid(gate):
    gate.on()
    time.sleep(PULSE_TIME)
    gate.off()

# --- START MUSIC BEFORE MAIN LOOP ---
start_music()

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
                    play_sound("jackpot")
            elif e.key == pygame.K_b:
                balls_left -= 1
            elif e.key == pygame.K_r:
                score, balls_left, collected, mega_jackpot = 0, 2, 0, False
            elif e.key == pygame.K_d:
                debug_mode = not debug_mode
            elif e.key == pygame.K_m:
                music_on = not music_on
                if music_on:
                    pygame.mixer.music.unpause()
                    print("🎵 Music ON")
                else:
                    pygame.mixer.music.pause()
                    print("🔇 Music OFF")

    # --- Physical targets ---
    if USE_GPIO:
        # Strike plates
        if targets_any.is_pressed:
            on_target_hit()
            time.sleep(0.25)
        # Bumpers
        if bumper1.is_pressed:
            on_bumper_hit(1)
            time.sleep(0.1)
        if bumper2.is_pressed:
            on_bumper_hit(2)
            time.sleep(0.1)

    # --- Simulated test key (ENTER) ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
        on_target_hit()
        pygame.time.wait(200)

    draw_layout()
    pygame.display.flip()
    clock.tick(60)

# --- CLEAN EXIT ---
targets_any.close()
bumper1.close()
bumper2.close()
gate1.close()
gate2.close()
pygame.quit()
sys.exit()
