from reader import SerialReader
import pygame
import sys

pygame.init()

# Fullscreen settings
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("MicroRogue")

clock = pygame.time.Clock()

# Colours
BACKGROUND = (25, 25, 30)
FLOOR_COLOUR = (90, 90, 100)
PLAYER_COLOUR = (180, 180, 190)
WHITE = (230, 230, 230)

# Floor
FLOOR_HEIGHT = 100
FLOOR_Y = SCREEN_HEIGHT - FLOOR_HEIGHT

# Player
PLAYER_SIZE = 48

player_x = 150.0
player_y = 100.0

player = pygame.Rect(
    int(player_x),
    int(player_y),
    PLAYER_SIZE,
    PLAYER_SIZE
)

# Physics
player_velocity_x = 0.0
player_velocity_y = 0.0

GRAVITY = 1200.0
JUMP_STRENGTH = -550.0
MOVE_SPEED = 350.0
DASH_SPEED = 900.0
DASH_DURATION = 0.15
DASH_COOLDOWN = 0.8

player_facing = 1
dash_timer = 0.0
dash_cooldown = 0.0
dash_direction = 1
dash_requested = False

# Jump reliability
grounded = False
coyote_time = 0.0
jump_buffer = 0.0

COYOTE_DURATION = 0.12
JUMP_BUFFER_DURATION = 0.12

# UI
font = pygame.font.Font(None, 28)

# Data from serial port
serial_reader = SerialReader()
serial_reader.Start()

# Game loop
running = True

while running:
    dt = min(clock.tick(60) / 1000, 0.05)

    # Events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            # Buffer jump input
            if event.key == pygame.K_SPACE or event.key == pygame.K_w :
                jump_buffer = JUMP_BUFFER_DURATION

            if event.key == pygame.K_LSHIFT:
                dash_requested = True

    # Input
    keys = pygame.key.get_pressed()

    movement_x = 0

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        movement_x -= 1

    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        movement_x += 1

    if movement_x:
        player_facing = movement_x

    dash_cooldown = max(0, dash_cooldown - dt)

    if dash_requested and dash_cooldown <= 0 and dash_timer <= 0:
        dash_timer = DASH_DURATION
        dash_cooldown = DASH_COOLDOWN
        dash_direction = player_facing

    dash_requested = False

    # Update coyote time
    if grounded:
        coyote_time = COYOTE_DURATION
    else:
        coyote_time = max(0, coyote_time - dt)

    # Update jump buffer
    jump_buffer = max(0, jump_buffer - dt)

    # Jump
    if jump_buffer > 0 and coyote_time > 0:
        player_velocity_y = JUMP_STRENGTH
        grounded = False
        coyote_time = 0
        jump_buffer = 0

    # Horizontal physics
    if dash_timer > 0:
        player_velocity_x = dash_direction * DASH_SPEED
        dash_timer = max(0, dash_timer - dt)
    else:
        player_velocity_x = movement_x * MOVE_SPEED

    player_x += player_velocity_x * dt

    # Screen boundary collisions (left and right)
    if player_x < 0:
        player_x = 0
        player_velocity_x = 0

    if player_x + PLAYER_SIZE > SCREEN_WIDTH:
        player_x = SCREEN_WIDTH - PLAYER_SIZE
        player_velocity_x = 0

    # Vertical physics
    previous_bottom = player_y + PLAYER_SIZE

    player_velocity_y += GRAVITY * dt
    player_y += player_velocity_y * dt

    new_bottom = player_y + PLAYER_SIZE

    # Floor collision
    grounded = False

    if player_velocity_y >= 0 and (
        previous_bottom <= FLOOR_Y <= new_bottom
        or player_y + PLAYER_SIZE >= FLOOR_Y
    ):
        player_y = FLOOR_Y - PLAYER_SIZE
        player_velocity_y = 0
        grounded = True

    # Ceiling collision
    if player_y < 0:
        player_y = 0
        player_velocity_y = 0

    # Update player rectangle for rendering and collision
    player.x = round(player_x)
    player.y = round(player_y)

    # Drawing
    screen.fill(BACKGROUND)

    # Floor
    pygame.draw.rect(
        screen,
        FLOOR_COLOUR,
        (0, FLOOR_Y, SCREEN_WIDTH, FLOOR_HEIGHT)
    )

    # Player
    pygame.draw.rect(screen, PLAYER_COLOUR, player)

    # Instructions
    text = font.render(
        "A/D or Arrows: Move | SPACE: Jump | LEFT SHIFT: Dash | ESC: Exit",
        True,
        WHITE
    )
    screen.blit(text, (30, 30))
    
    serial_data = serial_reader.GetSerialData()
    serial_text = font.render(
        f"Temp: {serial_data["temp"]} | Light: {serial_data["light"]} | Dir: {serial_data["dir"]}",
        True,
        WHITE
    )
    screen.blit(serial_text, (30, 60))


    pygame.display.flip()

pygame.quit()
sys.exit()
