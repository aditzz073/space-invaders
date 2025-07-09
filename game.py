import pygame
import random
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 700
PLAYER_SPEED = 7
BULLET_SPEED = -8
ENEMY_SPEED = 1
ENEMY_DROP = 30

# Colors - Modern color palette
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_BLUE = (4, 217, 255)
NEON_PINK = (255, 20, 147)
DARK_BLUE = (8, 28, 65)
SPACE_BLUE = (15, 15, 35)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
RED = (255, 50, 50)

# Particle system
particles = []

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 Space Invaders - Enhanced Edition")

# Load assets
player_img = pygame.image.load("player.png")
player_img = pygame.transform.scale(player_img, (50, 40))
enemy_img = pygame.image.load("enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (40, 40))

# Fonts - Multiple font sizes for better hierarchy
title_font = pygame.font.Font(None, 64)
score_font = pygame.font.Font(None, 32)
ui_font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 20)

# Stars for background
stars = []
for _ in range(100):
    stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)])

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Player properties
player_x = WIDTH // 2
player_y = HEIGHT - 80
player_dx = 0
player_health = 3
max_health = 3

# Bullet properties
bullets = []

# Enemy properties
enemies = []
for i in range(4):
    for j in range(8):
        enemies.append([80 + j * 80, 80 + i * 60])

# Explosion effects
explosions = []

class Particle:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.life = 30
        
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = max(0, min(255, self.life * 8))
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)

def create_explosion(x, y):
    for _ in range(10):
        velocity = [random.uniform(-3, 3), random.uniform(-3, 3)]
        color = random.choice([NEON_PINK, NEON_BLUE, CYAN, GOLD])
        particles.append(Particle(x, y, color, velocity))

def update_particles():
    global particles
    for particle in particles[:]:
        particle.update()
        if particle.life <= 0:
            particles.remove(particle)

def draw_particles():
    for particle in particles:
        particle.draw(screen)

def draw_starfield():
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[2])
        star[1] += star[2] * 0.5
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)

def draw_enemies():
    for enemy in enemies:
        # Add glow effect to enemies
        glow_rect = pygame.Rect(enemy[0] - 2, enemy[1] - 2, 44, 44)
        pygame.draw.rect(screen, NEON_GREEN, glow_rect, 2)
        screen.blit(enemy_img, (enemy[0], enemy[1]))

def move_enemies():
    global enemies, running, ENEMY_SPEED, player_health
    move_down = False
    for enemy in enemies:
        enemy[0] += ENEMY_SPEED
        if enemy[0] >= WIDTH - 40 or enemy[0] <= 0:
            move_down = True
    if move_down:
        for enemy in enemies:
            enemy[1] += ENEMY_DROP
        ENEMY_SPEED = -ENEMY_SPEED
    for enemy in enemies:
        if enemy[1] >= HEIGHT - 120:
            player_health = 0
            return

def check_collision(score):
    global bullets, enemies, player_health
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if enemy[0] < bullet[0] < enemy[0] + 40 and enemy[1] < bullet[1] < enemy[1] + 40:
                create_explosion(enemy[0] + 20, enemy[1] + 20)
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 10
                break
    return score

def draw_hud(score):
    # Background panel for HUD
    hud_rect = pygame.Rect(0, 0, WIDTH, 50)
    pygame.draw.rect(screen, DARK_BLUE, hud_rect)
    pygame.draw.line(screen, CYAN, (0, 50), (WIDTH, 50), 2)
    
    # Score display
    score_text = score_font.render(f"SCORE: {score:06d}", True, GOLD)
    screen.blit(score_text, (20, 15))
    
    # Health display
    health_text = ui_font.render("SHIELDS:", True, CYAN)
    screen.blit(health_text, (WIDTH - 200, 15))
    
    # Health bars
    for i in range(max_health):
        x = WIDTH - 120 + i * 30
        if i < player_health:
            pygame.draw.rect(screen, NEON_GREEN, (x, 18, 25, 15))
            pygame.draw.rect(screen, CYAN, (x, 18, 25, 15), 2)
        else:
            pygame.draw.rect(screen, RED, (x, 18, 25, 15), 2)

def draw_menu():
    # Gradient background
    for y in range(HEIGHT):
        color_ratio = y / HEIGHT
        r = int(SPACE_BLUE[0] * (1 - color_ratio) + BLACK[0] * color_ratio)
        g = int(SPACE_BLUE[1] * (1 - color_ratio) + BLACK[1] * color_ratio)
        b = int(SPACE_BLUE[2] * (1 - color_ratio) + BLACK[2] * color_ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    draw_starfield()
    
    # Title with glow effect
    title_text = title_font.render("SPACE INVADERS", True, CYAN)
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//3))
    
    # Draw glow
    for offset in range(1, 4):
        glow_text = title_font.render("SPACE INVADERS", True, DARK_BLUE)
        screen.blit(glow_text, (title_rect.x - offset, title_rect.y - offset))
        screen.blit(glow_text, (title_rect.x + offset, title_rect.y + offset))
    
    screen.blit(title_text, title_rect)
    
    # Menu options
    start_text = score_font.render("PRESS SPACE TO START", True, NEON_GREEN)
    start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(start_text, start_rect)
    
    controls_text = ui_font.render("CONTROLS: ← → ARROWS TO MOVE, SPACE TO SHOOT", True, WHITE)
    controls_rect = controls_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    screen.blit(controls_text, controls_rect)

def draw_game_over(score):
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Game Over text
    game_over_text = title_font.render("GAME OVER", True, RED)
    game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//3))
    screen.blit(game_over_text, game_over_rect)
    
    # Final score
    final_score_text = score_font.render(f"FINAL SCORE: {score:06d}", True, GOLD)
    final_score_rect = final_score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(final_score_text, final_score_rect)
    
    # Restart option
    restart_text = ui_font.render("PRESS R TO RESTART OR ESC TO QUIT", True, CYAN)
    restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    screen.blit(restart_text, restart_rect)

def reset_game():
    global player_x, player_y, player_dx, player_health, bullets, enemies, score, particles, game_state
    player_x = WIDTH // 2
    player_y = HEIGHT - 80
    player_dx = 0
    player_health = max_health
    bullets.clear()
    particles.clear()
    enemies.clear()
    
    # Recreate enemies
    for i in range(4):
        for j in range(8):
            enemies.append([80 + j * 80, 80 + i * 60])
    
    score = 0
    game_state = PLAYING

# Game loop
clock = pygame.time.Clock()
running = True
score = 0

while running:
    if game_state == MENU:
        draw_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False
    
    elif game_state == PLAYING:
        # Gradient background
        for y in range(HEIGHT):
            color_ratio = y / HEIGHT
            r = int(SPACE_BLUE[0] * (1 - color_ratio) + BLACK[0] * color_ratio)
            g = int(SPACE_BLUE[1] * (1 - color_ratio) + BLACK[1] * color_ratio)  
            b = int(SPACE_BLUE[2] * (1 - color_ratio) + BLACK[2] * color_ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
        
        draw_starfield()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player_dx = -PLAYER_SPEED
                if event.key == pygame.K_RIGHT:
                    player_dx = PLAYER_SPEED
                if event.key == pygame.K_SPACE:
                    bullets.append([player_x + 25, player_y])
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    player_dx = 0
        
        # Move player
        player_x += player_dx
        player_x = max(0, min(WIDTH - 50, player_x))
        
        # Draw player with glow effect
        glow_rect = pygame.Rect(player_x - 2, player_y - 2, 54, 44)
        pygame.draw.rect(screen, NEON_BLUE, glow_rect, 2)
        screen.blit(player_img, (player_x, player_y))
        
        # Move bullets
        for bullet in bullets[:]:
            bullet[1] += BULLET_SPEED
            if bullet[1] < 0:
                bullets.remove(bullet)
        
        # Move enemies
        move_enemies()
        score = check_collision(score)
        
        # Update particles
        update_particles()
        
        # Draw enhanced bullets
        for bullet in bullets:
            # Draw bullet trail
            pygame.draw.circle(screen, CYAN, (bullet[0] + 2, bullet[1] + 8), 4)
            pygame.draw.circle(screen, WHITE, (bullet[0] + 2, bullet[1] + 8), 2)
            # Add glow effect
            pygame.draw.circle(screen, NEON_BLUE, (bullet[0] + 2, bullet[1] + 8), 6, 1)
        
        draw_enemies()
        draw_particles()
        draw_hud(score)
        
        # Check win condition
        if not enemies:
            # Player wins this wave - could add more waves here
            score += 100
            reset_game()
        
        # Check game over condition
        if player_health <= 0:
            game_state = GAME_OVER
    
    elif game_state == GAME_OVER:
        draw_game_over(score)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False
    
    pygame.display.flip()
    clock.tick(60)  # Increased to 60 FPS for smoother gameplay

pygame.quit()
