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
player_img = pygame.image.load("assets/player.png")
player_img = pygame.transform.scale(player_img, (50, 40))
enemy_img = pygame.image.load("assets/enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (40, 40))

# Fonts - Custom aesthetic fonts with fallbacks
try:
    # Try to load system fonts for better aesthetics
    title_font = pygame.font.SysFont("orbitron", 72, bold=True)
    if not title_font:
        title_font = pygame.font.SysFont("arial", 72, bold=True)
except:
    title_font = pygame.font.Font(None, 72)

try:
    score_font = pygame.font.SysFont("consolas", 28, bold=True)
    if not score_font:
        score_font = pygame.font.SysFont("courier", 28, bold=True)
except:
    score_font = pygame.font.Font(None, 28)

try:
    ui_font = pygame.font.SysFont("arial", 22, bold=False)
except:
    ui_font = pygame.font.Font(None, 22)

try:
    small_font = pygame.font.SysFont("arial", 18, bold=False)
except:
    small_font = pygame.font.Font(None, 18)

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

def draw_text_with_shadow(surface, text, font, color, shadow_color, x, y, shadow_offset=2):
    """Draw text with a shadow effect for better readability and aesthetics"""
    # Draw shadow
    shadow_text = font.render(text, True, shadow_color)
    surface.blit(shadow_text, (x + shadow_offset, y + shadow_offset))
    
    # Draw main text
    main_text = font.render(text, True, color)
    surface.blit(main_text, (x, y))
    return main_text.get_rect(x=x, y=y)

def draw_text_with_glow(surface, text, font, color, glow_color, center_pos, glow_radius=3):
    """Draw text with a glowing effect"""
    # Draw multiple glow layers
    for i in range(glow_radius, 0, -1):
        alpha = max(30, 150 - i * 30)
        glow_surface = pygame.Surface(font.size(text), pygame.SRCALPHA)
        glow_text = font.render(text, True, (*glow_color, alpha))
        
        for dx in range(-i, i+1):
            for dy in range(-i, i+1):
                if dx*dx + dy*dy <= i*i:
                    text_rect = glow_text.get_rect(center=(center_pos[0] + dx, center_pos[1] + dy))
                    surface.blit(glow_text, text_rect)
    
    # Draw main text
    main_text = font.render(text, True, color)
    main_rect = main_text.get_rect(center=center_pos)
    surface.blit(main_text, main_rect)
    return main_rect

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
    # Background panel for HUD with gradient
    hud_rect = pygame.Rect(0, 0, WIDTH, 60)
    
    # Draw gradient background for HUD
    for y in range(60):
        alpha = int(200 * (1 - y / 60))
        color = (DARK_BLUE[0], DARK_BLUE[1], DARK_BLUE[2], alpha)
        pygame.draw.line(screen, DARK_BLUE, (0, y), (WIDTH, y))
    
    # Glow line separator
    pygame.draw.line(screen, CYAN, (0, 58), (WIDTH, 58), 3)
    pygame.draw.line(screen, NEON_BLUE, (0, 60), (WIDTH, 60), 1)
    
    # Score display with shadow
    score_text = f"SCORE: {score:06d}"
    draw_text_with_shadow(screen, score_text, score_font, GOLD, BLACK, 25, 18)
    
    # Health display with shadow
    draw_text_with_shadow(screen, "SHIELDS:", ui_font, CYAN, BLACK, WIDTH - 200, 20)
    
    # Enhanced health bars with glow effect
    for i in range(max_health):
        x = WIDTH - 120 + i * 32
        y = 22
        
        if i < player_health:
            # Draw glow effect for active shields
            pygame.draw.rect(screen, NEON_GREEN, (x-1, y-1, 27, 17), 0)
            pygame.draw.rect(screen, (0, 150, 0), (x+1, y+1, 23, 13), 0)
            pygame.draw.rect(screen, CYAN, (x, y, 25, 15), 2)
        else:
            # Draw depleted shields
            pygame.draw.rect(screen, (50, 0, 0), (x, y, 25, 15), 0)
            pygame.draw.rect(screen, RED, (x, y, 25, 15), 2)

def draw_menu():
    # Gradient background
    for y in range(HEIGHT):
        color_ratio = y / HEIGHT
        r = int(SPACE_BLUE[0] * (1 - color_ratio) + BLACK[0] * color_ratio)
        g = int(SPACE_BLUE[1] * (1 - color_ratio) + BLACK[1] * color_ratio)
        b = int(SPACE_BLUE[2] * (1 - color_ratio) + BLACK[2] * color_ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    draw_starfield()
    
    # Enhanced title with multiple glow effects
    title_center = (WIDTH//2, HEIGHT//3)
    draw_text_with_glow(screen, "SPACE INVADERS", title_font, CYAN, NEON_BLUE, title_center, 4)
    
    # Animated start button (subtle pulsing effect)
    pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.3 + 0.7
    start_color = (int(NEON_GREEN[0] * pulse), int(NEON_GREEN[1] * pulse), int(NEON_GREEN[2] * pulse))
    
    start_center = (WIDTH//2, HEIGHT//2)
    draw_text_with_shadow(screen, "PRESS SPACE TO START", score_font, start_color, BLACK, 
                         start_center[0] - score_font.size("PRESS SPACE TO START")[0]//2, 
                         start_center[1] - score_font.size("PRESS SPACE TO START")[1]//2, 3)
    
    # Controls text with better styling
    controls_center = (WIDTH//2, HEIGHT//2 + 60)
    draw_text_with_shadow(screen, "CONTROLS: ← → ARROWS TO MOVE, SPACE TO SHOOT", ui_font, WHITE, DARK_BLUE,
                         controls_center[0] - ui_font.size("CONTROLS: ← → ARROWS TO MOVE, SPACE TO SHOOT")[0]//2,
                         controls_center[1] - ui_font.size("CONTROLS: ← → ARROWS TO MOVE, SPACE TO SHOOT")[1]//2, 1)

def draw_game_over(score):
    # Semi-transparent overlay with better opacity
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Enhanced Game Over text with dramatic glow
    game_over_center = (WIDTH//2, HEIGHT//3)
    draw_text_with_glow(screen, "GAME OVER", title_font, RED, NEON_PINK, game_over_center, 5)
    
    # Final score with elegant styling
    final_score_text = f"FINAL SCORE: {score:06d}"
    final_score_center = (WIDTH//2, HEIGHT//2)
    draw_text_with_shadow(screen, final_score_text, score_font, GOLD, BLACK,
                         final_score_center[0] - score_font.size(final_score_text)[0]//2,
                         final_score_center[1] - score_font.size(final_score_text)[1]//2, 3)
    
    # Restart instructions with better spacing
    restart_text = "PRESS R TO RESTART OR ESC TO QUIT"
    restart_center = (WIDTH//2, HEIGHT//2 + 70)
    draw_text_with_shadow(screen, restart_text, ui_font, CYAN, DARK_BLUE,
                         restart_center[0] - ui_font.size(restart_text)[0]//2,
                         restart_center[1] - ui_font.size(restart_text)[1]//2, 2)

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

def draw_starfield():
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[2])
        star[1] += star[2] * 0.5
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)

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
