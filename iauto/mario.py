import sys

import pygame

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BG_COLOR = (107, 140, 255)  # Sky blue
GROUND_HEIGHT = SCREEN_HEIGHT - 60
PLAYER_COLOR = (255, 0, 0)  # Red color
PLAYER_START_POS = (50, GROUND_HEIGHT - 30)
GRAVITY = 1
JUMP_HEIGHT = -100
MOVE_SPEED = 10
OBSTACLE_COLOR = (0, 0, 0)  # Black color
ENEMY_COLOR = (255, 255, 0)  # Yellow color, representing the moving enemies
HEALTH = 3  # New constant for player's health

# Obstacles
obstacles = [
    pygame.Rect(300, GROUND_HEIGHT - 50, 50, 50),
    pygame.Rect(550, GROUND_HEIGHT - 100, 50, 100),
    pygame.Rect(700, GROUND_HEIGHT - 30, 100, 30)
]

# Enemies
enemies = [
    {'rect': pygame.Rect(600, GROUND_HEIGHT - 50, 30, 30), 'speed': 2},
]

# Setup the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Super Mario Game')

# Player properties
player_pos = list(PLAYER_START_POS)
player_vel = [0, 0]
player_rect = pygame.Rect(*player_pos, 30, 30)
on_ground = True

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Key states for continuous movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_pos[0] -= MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            player_pos[0] += MOVE_SPEED
        if keys[pygame.K_SPACE] and on_ground:
            player_vel[1] = JUMP_HEIGHT
            on_ground = False

    # Update player rect for collision
    player_rect.topleft = player_pos

    # Player physics
    player_vel[1] += GRAVITY
    player_pos[1] += player_vel[1]
    if player_pos[1] >= GROUND_HEIGHT - 30:
        player_pos[1] = GROUND_HEIGHT - 30
        player_vel[1] = 0
        on_ground = True

    # Check collision with obstacles
    for obstacle in obstacles:
        if player_rect.colliderect(obstacle):
            if player_vel[1] > 0:  # Falling down
                player_pos[1] = obstacle.top - 30
                player_vel[1] = 0
                on_ground = True

    # Move enemies and check collision with player
    for enemy in enemies:
        enemy['rect'].x += enemy['speed']
        if enemy['rect'].right > SCREEN_WIDTH or enemy['rect'].left < 0:
            enemy['speed'] *= -1  # Change direction when hitting screen bounds
        if player_rect.colliderect(enemy['rect']):
            HEALTH -= 1
            if HEALTH == 0:
                print("Game Over")  # Simple game over message
                running = False
            player_pos = list(PLAYER_START_POS)  # Reset player position

    # Drawing
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
    pygame.draw.rect(screen, (0, 255, 0), (0, GROUND_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT))
    # Draw obstacles
    for obstacle in obstacles:
        pygame.draw.rect(screen, OBSTACLE_COLOR, obstacle)
    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, ENEMY_COLOR, enemy['rect'])

    # Update screen
    pygame.display.flip()
    clock.tick(60)

# Quit the game
pygame.quit()
sys.exit()
