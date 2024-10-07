import pygame
import random 
import xml.etree.ElementTree as ET

#Initialize Pygame
pygame.init()

# set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game")

#Load images
spritesheet = pygame.image.load("spritesheet_vehicles.png")
road_image = pygame.image.load("road.png")

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Parse XML file
tree = ET.parse('spritesheet_vehicles.xml')
root = tree.getroot()


# Create a dictionary to store vehicle sprites
vehicles = {}
for subtexture in root.findall('SubTexture'):
    name = subtexture.get('name')
    x = int(subtexture.get('x'))
    y = int(subtexture.get('y'))
    width = int(subtexture.get('width'))
    height = int(subtexture.get('height'))
    vehicles[name] = (x, y, width, height)

# Car properties
player_car_name = "car_green_4.png"
player_car_rect = vehicles[player_car_name]
CAR_WIDTH = 60
CAR_HEIGHT = 100
player_car = pygame.Surface((player_car_rect[2], player_car_rect[3]), pygame.SRCALPHA)
player_car.blit(spritesheet, (0, 0), player_car_rect)
player_car = pygame.transform.scale(player_car, (CAR_WIDTH, CAR_HEIGHT))

# Lane properties
LANE_COUNT = 4
LANE_WIDTH = WIDTH // LANE_COUNT
current_lane = LANE_COUNT // 2
car_x = (current_lane * LANE_WIDTH) + (LANE_WIDTH - CAR_WIDTH) // 2
car_y = HEIGHT - CAR_HEIGHT - 20

# Obstacle properties
OBSTACLE_WIDTH = 60
OBSTACLE_HEIGHT = 100
obstacle_speed = 5
obstacles = []

# Road properties
road_y = 0
road_speed = 5

# Game variables
score = 0
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Game states
PLAYING = 0
GAME_OVER = 1
game_state = PLAYING

def get_random_car():
    car_name = random.choice([name for name in vehicles.keys() if name.startswith("car_") and not name.endswith("small_1.png") and not "green" in name])
    car_rect = vehicles[car_name]
    car_surface = pygame.Surface((car_rect[2], car_rect[3]), pygame.SRCALPHA)
    car_surface.blit(spritesheet, (0, 0), car_rect)
    return pygame.transform.scale(car_surface, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

def show_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black overlay
    screen.blit(overlay, (0, 0))

    game_over_text = large_font.render("GAME OVER", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))

    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))

    restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT * 2 // 3, 200, 50)
    pygame.draw.rect(screen, GREEN, restart_button)
    restart_text = font.render("Restart", True, BLACK)
    screen.blit(restart_text, (restart_button.centerx - restart_text.get_width() // 2, restart_button.centery - restart_text.get_height() // 2))

    return restart_button


def reset_game():
    global current_lane, car_x, car_y, obstacles, score, game_state, road_y
    current_lane = LANE_COUNT // 2
    car_x = (current_lane * LANE_WIDTH) + (LANE_WIDTH - CAR_WIDTH) // 2
    car_y = HEIGHT - CAR_HEIGHT - 20
    obstacles = []
    score = 0
    game_state = PLAYING
    road_y = 0

#Game Loop

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and game_state == PLAYING:
            if event.key == pygame.K_LEFT and current_lane > 0:
                current_lane -= 1
            elif event.key == pygame.K_RIGHT and current_lane < LANE_COUNT - 1:
                current_lane += 1
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state == GAME_OVER:
            if restart_button.collidepoint(event.pos):
                reset_game()
    
    if game_state == PLAYING:
        # Update car position
        target_x = (current_lane * LANE_WIDTH) + (LANE_WIDTH - CAR_WIDTH) // 2
        car_x += (target_x - car_x) * 0.2  # Smooth movement
        # Create new obstacles
        if len(obstacles) < 5 and random.randint(1, 60) == 1:
            lane = random.randint(0, LANE_COUNT - 1)
            obstacle_x = (lane * LANE_WIDTH) + (LANE_WIDTH - OBSTACLE_WIDTH) // 2
            obstacle_y = -OBSTACLE_HEIGHT
            obstacle_car = get_random_car()
            # Check for overlap with existing obstacles
            overlap = any(abs(obstacle[1] - obstacle_y) < OBSTACLE_HEIGHT * 1.5 for obstacle in obstacles if obstacle[0] == obstacle_x)
            if not overlap:
                obstacles.append([obstacle_x, obstacle_y, obstacle_car])
        
        # Move and remove obstacles
        for obstacle in obstacles[:]:
            obstacle[1] += obstacle_speed
            if obstacle[1] > HEIGHT:
                obstacles.remove(obstacle)
                score +=1
                
        # Check for collisions
        player_rect = pygame.Rect(car_x, car_y, CAR_WIDTH, CAR_HEIGHT)
        for obstacle in obstacles:
            obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
            if player_rect.colliderect(obstacle_rect):
                game_state = GAME_OVER
        # Scroll the road
        road_y = (road_y + road_speed) % road_image.get_height()

        # clear the screen
        screen.fill(BLACK)
        # Draw the scrolling road
        screen.blit(road_image, (0, road_y - road_image.get_height()))
        screen.blit(road_image, (0, road_y))
        # Draw lane dividers
        for i in range(1, LANE_COUNT):
            pygame.draw.line(screen, WHITE, (i * LANE_WIDTH, 0), (i * LANE_WIDTH, HEIGHT), 2)
        # Draw the player's car
        screen.blit(player_car, (int(car_x), car_y))
       # Draw obstacles
        for obstacle in obstacles:
            screen.blit(obstacle[2], (obstacle[0], obstacle[1]))

        #show the score
        show_score()
    elif game_state == GAME_OVER:
        restart_button = draw_game_over()

    
    #update the display 
    pygame.display.flip()

    #Control the game speed
    clock.tick(60)

# Quit the game

pygame.quit()


        

