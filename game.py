import pygame
import random
import math
import os

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Swamp Defense")

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# File for highscore
highscore_file = "highscore.txt"

# Load the highscore from file
def load_highscore():
    if os.path.exists(highscore_file):
        with open(highscore_file, "r") as file:
            return int(file.read())
    else:
        return 0

# Save the highscore to file
def save_highscore(score):
    with open(highscore_file, "w") as file:
        file.write(str(score))

# Game variables
money = 0
fire_rate = 500  # Milliseconds
bullet_damage = 5
last_shot = 0
spawn_rate = 2000  # Milliseconds
last_spawn = 0
player_x = 50
player_y = HEIGHT // 2
cone_max_angle = math.radians(45)  # Always 45 degrees
cone_length = 300

# Score & Level
score = 0
level = 1
score_to_level_up = 10  # Points per level
highscore = load_highscore()  # Load the highscore

# Player health
health = 5  # Start with 5 health

# Upgrade levels
damage_level = 1
spread_level = 1
range_level = 1

# Upgrade costs
upgrade_costs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Price for buying life
life_price = 5  # Cost of 1 extra life

# Upgrade functions
def upgrade_damage():
    global bullet_damage, damage_level, money
    if damage_level < 5 and money >= upgrade_costs[damage_level - 1]:
        money -= upgrade_costs[damage_level - 1]
        damage_level += 1
        bullet_damage = 5 + (damage_level - 1) * 2.5

def upgrade_spread():
    global cone_max_angle, spread_level, money
    if spread_level < 10 and money >= upgrade_costs[spread_level - 1]:
        money -= upgrade_costs[spread_level - 1]
        spread_level += 1
        cone_max_angle = math.radians(45 - (spread_level - 1) * 3)

def upgrade_range():
    global cone_length, range_level, money
    if range_level < 5 and money >= upgrade_costs[range_level - 1]:
        money -= upgrade_costs[range_level - 1]
        range_level += 1
        cone_length = 300 + (range_level - 1) * 50

# Function to buy life
def buy_life():
    global money, health
    if money >= life_price:
        money -= life_price
        health += 1  # Increase health by 1 when buying

# Zombie class
class Zombie:
    def __init__(self, level):
        self.x = random.randint(WIDTH - 200, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.speed = random.uniform(1, 3) + (level * 0.2)  # Increase speed with level
        self.hp = 10 + (level * 5)  # Increase HP with level
        self.alive = True

    def move(self):
        self.x -= self.speed
        if self.x < 50:  # If zombie reaches left side, player loses health
            global health
            health -= 1
            self.alive = False  # Zombie is removed after it hits the player

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, 40, 40))

# Pellet class
class Pellet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.distance_traveled = 0
        self.max_distance = cone_length

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.distance_traveled += self.speed

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 5)

# Start Screen
def show_start_screen():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 48)
    title_text = font.render("Swamp Defense", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

    font = pygame.font.Font(None, 36)
    start_text = font.render("Press ENTER to Start", True, BLACK)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))

    highscore_text = font.render(f"Highscore: {highscore}", True, BLACK)
    screen.blit(highscore_text, (WIDTH // 2 - highscore_text.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()

# Game loop
running = True
game_started = False
zombies = []
pellets = []
clock = pygame.time.Clock()

while running:
    if not game_started:
        # Show start screen
        show_start_screen()
    else:
        if health <= 0:
            # Game Over screen
            screen.fill(WHITE)
            font = pygame.font.Font(None, 48)
            game_over_text = font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))

            font = pygame.font.Font(None, 36)
            final_score_text = font.render(f"Final Score: {score}", True, BLACK)
            screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2))

            pygame.display.flip()

            # Wait for a key press to restart or quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Reset the game
                        score = 0
                        health = 5
                        level = 1
                        money = 0
                        zombies = []
                        pellets = []
                        game_started = False  # Go back to the start screen

        else:
            # Main game logic here
            screen.fill(WHITE)
            current_time = pygame.time.get_ticks()
            mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my - player_y, mx - player_x)
            spread_range = cone_max_angle / 2  # Always fixed at max 45 degrees, reducing with upgrades

            # Spawn zombies with level scaling
            if current_time - last_spawn > spawn_rate:
                zombies.append(Zombie(level))  # Pass current level to scale zombie attributes
                last_spawn = current_time

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and current_time - last_shot > fire_rate:
                        last_shot = current_time
                        for i in range(7):
                            spread = angle + random.uniform(-spread_range, spread_range)
                            pellets.append(Pellet(player_x, player_y, spread))
                    if event.key == pygame.K_1:
                        upgrade_damage()
                    if event.key == pygame.K_2:
                        upgrade_spread()
                    if event.key == pygame.K_3:
                        upgrade_range()
                    if event.key == pygame.K_b:  # Press B to buy life
                        buy_life()

            # Move pellets and check for hits
            for p in pellets[:]:
                p.move()
                if p.distance_traveled > p.max_distance:
                    pellets.remove(p)
                    continue
                for z in zombies[:]:
                    if z.x < p.x < z.x + 40 and z.y < p.y < z.y + 40:
                        z.hp -= bullet_damage
                        pellets.remove(p)
                        if z.hp <= 0:
                            zombies.remove(z)
                            money += 1
                            score += 1  # Increase score when killing a zombie
                        break
                else:
                    p.draw()

            # Move zombies
            for z in zombies[:]:
                z.move()
                if not z.alive:
                    zombies.remove(z)
                z.draw()

            # Draw shooting cone
            cone_end1 = (
                player_x + cone_length * math.cos(angle - spread_range),
                player_y + cone_length * math.sin(angle - spread_range)
            )
            cone_end2 = (
                player_x + cone_length * math.cos(angle + spread_range),
                player_y + cone_length * math.sin(angle + spread_range)
            )
            pygame.draw.polygon(screen, YELLOW, [(player_x, player_y), cone_end1, cone_end2], 1)

            # Display money
            font = pygame.font.Font(None, 36)
            money_text = font.render(f"Gold: {money}", True, BLACK)
            screen.blit(money_text, (10, 10))

            # Display upgrades
            upgrade_text = font.render("1: Damage | 2: Spread | 3: Range", True, BLACK)
            screen.blit(upgrade_text, (10, HEIGHT - 30))

            # Display Score & Level
            score_text = font.render(f"Score: {score}", True, BLACK)
            level_text = font.render(f"Level: {level}", True, BLACK)
            screen.blit(score_text, (WIDTH - 150, 10))
            screen.blit(level_text, (WIDTH - 150, 40))

            # Display Health
            health_text = font.render(f"Health: {health}", True, BLACK)
            screen.blit(health_text, (WIDTH - 150, 70))

            # Display Life purchase option
            buy_life_text = font.render(f"Press B to Buy Life (Cost: {life_price} Gold)", True, BLACK)
            screen.blit(buy_life_text, (10, HEIGHT - 60))

            # Level up when reaching required score
            if score >= score_to_level_up * level:
                level += 1
                print(f"Level Up! Now at Level {level}")

            # Display Highscore
            highscore_text = font.render(f"Highscore: {highscore}", True, BLACK)
            screen.blit(highscore_text, (WIDTH - 150, 100))

            # Update Highscore if necessary
            if score > highscore:
                highscore = score
                save_highscore(highscore)  # Save new highscore

            pygame.display.flip()

    # Event handling for start screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if not game_started and event.key == pygame.K_RETURN:
                game_started = True  # Start the game when ENTER is pressed

    clock.tick(60)

pygame.quit()
