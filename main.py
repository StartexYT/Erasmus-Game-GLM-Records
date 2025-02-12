import pygame
import random
import math

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

# Upgrade levels
damage_level = 1
spread_level = 1
range_level = 1

# Upgrade costs
upgrade_costs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


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


# Zombie class
class Zombie:
    def __init__(self):
        self.x = random.randint(WIDTH - 200, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.speed = random.uniform(1, 3)
        self.hp = 10
        self.alive = True

    def move(self):
        self.x -= self.speed
        if self.x < 50:
            self.alive = False

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


# Game loop
running = True
zombies = []
pellets = []
clock = pygame.time.Clock()
while running:
    screen.fill(WHITE)
    current_time = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    angle = math.atan2(my - player_y, mx - player_x)
    spread_range = cone_max_angle / 2  # Always fixed at max 45 degrees, reducing with upgrades

    if current_time - last_spawn > spawn_rate:
        zombies.append(Zombie())
        last_spawn = current_time

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
                break
        else:
            p.draw()

    for z in zombies[:]:
        z.move()
        if not z.alive:
            zombies.remove(z)
        z.draw()

    cone_end1 = (
    player_x + cone_length * math.cos(angle - spread_range), player_y + cone_length * math.sin(angle - spread_range))
    cone_end2 = (
    player_x + cone_length * math.cos(angle + spread_range), player_y + cone_length * math.sin(angle + spread_range))
    pygame.draw.polygon(screen, YELLOW, [(player_x, player_y), cone_end1, cone_end2], 1)

    font = pygame.font.Font(None, 36)
    money_text = font.render(f"Gold: {money}", True, BLACK)
    screen.blit(money_text, (10, 10))

    upgrade_text = font.render("1: Damage | 2: Spread | 3: Range", True, BLACK)
    screen.blit(upgrade_text, (10, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
