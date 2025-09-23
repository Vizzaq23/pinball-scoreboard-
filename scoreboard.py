import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pinball Scoreboard Mock")

# Fonts
title_font = pygame.font.Font(None, 80)
score_font = pygame.font.Font(None, 120)
small_font = pygame.font.Font(None, 50)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Game variables
score = 0
high_score = 0
balls_left = 3
current_player = 1

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Simulate play with SPACE key
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                score += 100
                if score > high_score:
                    high_score = score

            # Simulate ball drain with "B"
            if event.key == pygame.K_b:
                balls_left -= 1
                if balls_left == 0:
                    # Reset for next player
                    balls_left = 3
                    score = 0
                    current_player = 2 if current_player == 1 else 1

    # Clear screen
    screen.fill(BLACK)

    # Title
    title_text = title_font.render("PINBALL SCOREBOARD", True, GREEN)
    screen.blit(title_text, (100, 30))

    # Current score
    score_text = score_font.render(f"{score}", True, WHITE)
    screen.blit(score_text, (330, 200))

    # Balls left
    balls_text = small_font.render(f"Balls Left: {balls_left}", True, WHITE)
    screen.blit(balls_text, (50, 500))

    # Player
    player_text = small_font.render(f"Player {current_player}", True, WHITE)
    screen.blit(player_text, (600, 500))

    # High score
    high_score_text = small_font.render(f"High Score: {high_score}", True, RED)
    screen.blit(high_score_text, (280, 500))

    # Update display
    pygame.display.flip()

# Quit
pygame.quit()
sys.exit()
