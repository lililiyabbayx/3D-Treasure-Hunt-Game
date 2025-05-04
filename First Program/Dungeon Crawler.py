from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

# Game state variables
game_active = False
game_won = False
game_over = False
start_time = 0
total_time_limit = 120  # 2 minutes time limit

# Player variables
player_pos = [0, 0, 0]  # x, y, z
player_angle = 0
player_speed = 10
player_size = 30
player_health = 100
player_hidden = False  # Stealth mode
collected_treasures = 0
# Boost system
boost_active = False
boost_start_time = 0
boost_duration = 3       # Boost lasts 3 seconds
boost_cooldown = 9       # Time before you can boost again
last_boost_time = -boost_cooldown  # Ensure it's available at start

# Camera variables
camera_pos = (0, -200, 150)  # Initial camera position
camera_angle = 0
camera_height = 550
camera_distance = 500
third_person_view = True

# Map variables
MAP_SIZE = 1000
GRID_LENGTH = 600
WALL_HEIGHT = 100
obstacles = []  # List of obstacles [x, y, width, height]
treasures = []  # List of treasures [x, y, collected]
monsters = []   # List of monsters [x, y, direction, speed, patrol_points, current_target]

# Gameplay configuration
NUM_TREASURES = 5
NUM_MONSTERS = 3
NUM_OBSTACLES = 15
TOTAL_TREASURES_NEEDED = 5

# Lighting
light_enabled = True
ambient_light = [0.6, 0.6, 0.6, 1.0]  # Low ambient light for dungeon feel
diffuse_light = [1.0, 1.0, 1.0, 1.0]
light_position = [0, 0, 300, 1.0]


def init_game():
    """Initialize the game state with obstacles, treasures, and monsters."""
    global obstacles, treasures, monsters, player_pos, start_time
    global game_active, game_won, game_over, collected_treasures, player_health
    global boost_active, boost_start_time, last_boost_time,player_hidden

    # Reset game state
    obstacles = []
    treasures = []
    monsters = []
    player_pos = [0, 0, 20]
    player_health = 100
    collected_treasures = 0
    game_active = True
    game_won = False
    game_over = False
    if player_hidden:
        player_hidden=False
    start_time = time.time()
    # --- reset boost system ---
    boost_active = False
    boost_start_time = 0
    last_boost_time = start_time - boost_cooldown
    # Generate obstacles (walls)
    for _ in range(NUM_OBSTACLES):
        width = random.randint(50, 200)
        height = random.randint(50, 200)
        x = random.randint(-GRID_LENGTH + width//2, GRID_LENGTH - width//2)
        y = random.randint(-GRID_LENGTH + height//2, GRID_LENGTH - height//2)
        
        # Ensure no obstacle is too close to player start position
        if abs(x) < 100 and abs(y) < 100:
            continue
            
        obstacles.append([x, y, width, height])
    
    # Generate treasures
    for _ in range(NUM_TREASURES):
        while True:
            x = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            y = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            
            # Check if treasure is not inside any obstacle and not too close to player
            valid_position = True
            if abs(x) < 100 and abs(y) < 100:
                valid_position = False
                
            for ox, oy, width, height in obstacles:
                if (ox - width/2 <= x <= ox + width/2) and (oy - height/2 <= y <= oy + height/2):
                    valid_position = False
                    break
            
            if valid_position:
                treasures.append([x, y, False])  # x, y, collected status
                break
    
    # Generate monsters and their patrol routes
    for _ in range(NUM_MONSTERS):
        # Create patrol points
        patrol_points = []
        for _ in range(random.randint(3, 6)):
            px = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            py = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            patrol_points.append([px, py])
        
        # Initial position is first patrol point
        x, y = patrol_points[0]
        speed = random.uniform(0.3, 1.0)
        
        monsters.append([x, y, 0, speed, patrol_points, 0])  # x, y, direction, speed, patrol points, current target


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18): # type: ignore # type: ignore
    """Draw text at screen position (x, y)."""
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection for screen coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_player():
    """Draw the player character."""
    glPushMatrix()
    
    # Position the player
    glTranslatef(player_pos[0], player_pos[1], player_pos[2] + player_size/2)
    glRotatef(player_angle, 0, 0, 1)
    
    # Draw player body
    if player_hidden:
        # Translucent when in stealth mode
        glColor4f(0.3, 0.5, 0.8, 0.5)
    else:
        glColor3f(0.2, 0.4, 0.8)
    
    glutSolidSphere(player_size/2, 12, 12)
    
    # Draw player direction indicator (nose)
    glColor3f(1, 0, 0)
    glPushMatrix()
    glTranslatef(player_size/2, 0, 0)
    glutSolidSphere(player_size/5, 8, 8)
    glPopMatrix()
    
    glPopMatrix()


def draw_treasure_chest(x, y, collected):
    """Draw a treasure chest at position (x, y)."""
    glPushMatrix()
    glTranslatef(x, y, 15)
    
    if collected:
        # Draw open chest (collected)
        glColor3f(0.3, 0.2, 0.1)  # Dark brown base
    else:
        # Draw closed chest (not collected)
        glColor3f(0.8, 0.6, 0.2)  # Gold color
        
        # Draw shining effect
        if int(time.time() * 2) % 2 == 0:
            glPushMatrix()
            glTranslatef(0, 0, 30)
            glColor3f(1.0, 1.0, 0.6)
            glutSolidSphere(8, 8, 8)
            glPopMatrix()
    
    # Chest base
    glPushMatrix()
    glScalef(20, 15, 10)
    glutSolidCube(1)
    glPopMatrix()
    
    # Chest lid
    glPushMatrix()
    if collected:
        glTranslatef(-5, 0, 10)
        glRotatef(120, 0, 1, 0)
    else:
        glTranslatef(0, 0, 10)
    
    glColor3f(0.7, 0.5, 0.2)
    glScalef(20, 15, 5)
    glutSolidCube(1)
    glPopMatrix()
    
    glPopMatrix()


def draw_monster(x, y, direction):
    """Draw a monster at position (x, y)."""
    glPushMatrix()
    glTranslatef(x, y, 30)
    glRotatef(direction, 0, 0, 1)
    
    # Monster body
    glColor3f(0.7, 0.0, 0.0)  # Red
    glutSolidSphere(25, 10, 10)
    
    # Monster eyes
    glColor3f(1.0, 1.0, 0.0)  # Yellow
    
    glPushMatrix()
    glTranslatef(15, 10, 10)
    glutSolidSphere(5, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(15, -10, 10)
    glutSolidSphere(5, 8, 8)
    glPopMatrix()
    
    # Monster teeth
    glColor3f(1.0, 1.0, 1.0)  # White
    glPushMatrix()
    glTranslatef(22, 0, -5)
    glRotatef(90, 0, 1, 0)
    glutSolidCone(10, 10, 4, 1)
    glPopMatrix()
    
    glPopMatrix()


def draw_obstacle(x, y, width, height):
    """Draw an obstacle (wall) at position (x, y)."""
    glPushMatrix()
    glTranslatef(x, y, WALL_HEIGHT/2)
    
    # Set wall color
    glColor3f(0.5, 0.5, 0.6)  # Stone gray
    
    # Draw the wall
    glPushMatrix()
    glScalef(width, height, WALL_HEIGHT)
    glutSolidCube(1)
    glPopMatrix()
    
    # Add some stone texture detail
    glColor3f(0.4, 0.4, 0.5)  # Darker gray for details
    for _ in range(5):
        dx = random.uniform(-width/2.2, width/2.2)
        dy = random.uniform(-height/2.2, height/2.2)
        dz = random.uniform(-WALL_HEIGHT/2.2, WALL_HEIGHT/2.2)
        dsize = random.uniform(5, 15)
        
        glPushMatrix()
        glTranslatef(dx, dy, dz)
        glutSolidCube(dsize)
        glPopMatrix()
    
    glPopMatrix()


def draw_floor():
    """Draw the dungeon floor with a grid pattern."""
    cell_size = 50
    
    glBegin(GL_QUADS)
    
    for x in range(-GRID_LENGTH, GRID_LENGTH + 1, cell_size):
        for y in range(-GRID_LENGTH, GRID_LENGTH + 1, cell_size):
            # Alternate colors for grid cells
            if (x//cell_size + y//cell_size) % 2 == 0:
                glColor3f(0.3, 0.3, 0.35)  # Dark gray
            else:
                glColor3f(0.35, 0.35, 0.4)  # Slightly lighter gray
            
            glVertex3f(x, y, 0)
            glVertex3f(x + cell_size, y, 0)
            glVertex3f(x + cell_size, y + cell_size, 0)
            glVertex3f(x, y + cell_size, 0)
    
    glEnd()


def draw_dungeon_boundary():
    """Draw the outer walls of the dungeon."""
    # Draw outer walls
    wall_thickness = 20
    
    # North wall
    glPushMatrix()
    glTranslatef(0, GRID_LENGTH + wall_thickness/2, WALL_HEIGHT/2)
    glColor3f(0.4, 0.4, 0.45)
    glScalef(2*GRID_LENGTH + 2*wall_thickness, wall_thickness, WALL_HEIGHT)
    glutSolidCube(1)
    glPopMatrix()
    
    # South wall
    glPushMatrix()
    glTranslatef(0, -GRID_LENGTH - wall_thickness/2, WALL_HEIGHT/2)
    glColor3f(0.4, 0.4, 0.45)
    glScalef(2*GRID_LENGTH + 2*wall_thickness, wall_thickness, WALL_HEIGHT)
    glutSolidCube(1)
    glPopMatrix()
    
    # East wall
    glPushMatrix()
    glTranslatef(GRID_LENGTH + wall_thickness/2, 0, WALL_HEIGHT/2)
    glColor3f(0.4, 0.4, 0.45)
    glScalef(wall_thickness, 2*GRID_LENGTH, WALL_HEIGHT)
    glutSolidCube(1)
    glPopMatrix()
    
    # West wall
    glPushMatrix()
    glTranslatef(-GRID_LENGTH - wall_thickness/2, 0, WALL_HEIGHT/2)
    glColor3f(0.4, 0.4, 0.45)
    glScalef(wall_thickness, 2*GRID_LENGTH, WALL_HEIGHT)
    glutSolidCube(1)
    glPopMatrix()


def draw_status_bar():
    """Draw a 3D HUD status bar in the world."""
    # Draw status bar showing health and treasures
    x = player_pos[0] - 40
    y = player_pos[1] - 60
    z = player_pos[2] + 80
    
    # Health bar background
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.2, 0.2, 0.2)
    glScalef(82, 12, 1)
    glutSolidCube(1)
    glPopMatrix()
    
    # Health bar fill
    health_width = 80 * (player_health / 100)
    glPushMatrix()
    glTranslatef(x - (80 - health_width)/2, y, z + 1)
    
    # Color changes based on health level
    if player_health > 60:
        glColor3f(0.0, 0.8, 0.0)  # Green
    elif player_health > 30:
        glColor3f(0.8, 0.8, 0.0)  # Yellow
    else:
        glColor3f(0.8, 0.0, 0.0)  # Red
        
    glScalef(health_width, 10, 1)
    glutSolidCube(1)
    glPopMatrix()
    
    # Treasure indicators
    for i in range(TOTAL_TREASURES_NEEDED):
        glPushMatrix()
        glTranslatef(x + i*15 - 30, y - 15, z)
        
        if i < collected_treasures:
            glColor3f(0.8, 0.8, 0.0)  # Gold for collected
        else:
            glColor3f(0.4, 0.4, 0.4)  # Gray for not collected
            
        glutSolidCube(10)
        glPopMatrix()


def draw_game_ui():
    """Draw 2D UI elements that stay fixed on screen."""
    # Draw time remaining
    time_elapsed = int(time.time() - start_time)
    time_remaining = max(0, total_time_limit - time_elapsed)
    minutes = time_remaining // 60
    seconds = time_remaining % 60
    
    # Status messages
    if game_active:
        draw_text(10, 770, f"Time Remaining: {minutes:02d}:{seconds:02d}")
        draw_text(10, 740, f"Health: {player_health}%")
        draw_text(10, 710, f"Treasures: {collected_treasures}/{TOTAL_TREASURES_NEEDED}")
        
        if player_hidden:
            draw_text(10, 680, "STEALTH MODE ACTIVE")
    
    # Game over or win messages
    if game_over:
        draw_text(400, 400, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24) # type: ignore
        draw_text(350, 350, "Press R to restart")
    
    if game_won:
        draw_text(400, 400, "YOU WIN!", GLUT_BITMAP_TIMES_ROMAN_24) # type: ignore
        draw_text(330, 350, "All treasures collected!")
        draw_text(350, 320, "Press R to restart")
    
    if not game_active and not game_over and not game_won:
        # Start screen
        draw_text(380, 450, "DUNGEON CRAWLER", GLUT_BITMAP_TIMES_ROMAN_24) # type: ignore
        draw_text(250, 400, "Find all treasures before time runs out!")
        draw_text(280, 370, "Press SPACE to start the game")
        draw_text(200, 340, "Use W,A,S,D to move, C for stealth mode, shift for speed boost")
        draw_text(220, 310, "Avoid monsters and collect treasures!")
    if boost_active:
        draw_text(10, 650, "Speed Boost: ACTIVE")
    elif time.time() - last_boost_time < boost_cooldown:
        cd = int(boost_cooldown - (time.time() - last_boost_time))
        draw_text(10, 650, f"Speed Boost: Cooldown ({cd}s)")
    elif game_active:
        draw_text(10, 650, "Speed Boost: Ready")

# size of minimap in pixels
MINIMAP_W, MINIMAP_H = 200, 200

def draw_topdown_minimap():
    # 1. Set viewport to the lower‐right corner
    glViewport(1000 - MINIMAP_W, 0, MINIMAP_W, MINIMAP_H)
    glEnable(GL_SCISSOR_TEST)
    glScissor(1000 - MINIMAP_W, 0, MINIMAP_W, MINIMAP_H)
    # clear only depth so the map draws cleanly
    glClear(GL_DEPTH_BUFFER_BIT)
    
    # 2. Switch to a projection for a top‐down camera
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    # Could be orthographic or perspective; here we use a wide FOV:
    gluPerspective(90, MINIMAP_W / MINIMAP_H, 0.1, 2000)
    
    # 3. Position camera straight above the player
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    px, py, pz = player_pos
    # eye at (px, py, HIGH), look at (px,py,0), up=(0,1,0)
    gluLookAt(px, py, 800,
              px, py,   0,
              1,   0,   0)
    
    # 4. Draw the exact same 3D scene (floor, walls, treasures, monsters, player)
    #    You can call your existing draw_* routines (minus the 2D UI).
    draw_floor()
    draw_dungeon_boundary()
    for ox, oy, w, h in obstacles:    draw_obstacle(ox, oy, w, h)
    for tx, ty, col in treasures:     draw_treasure_chest(tx, ty, col)
    for mx_, my_, dir_, *_ in monsters: draw_monster(mx_, my_, dir_)
    draw_player()
    
    # 5. Restore matrices & state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glDisable(GL_SCISSOR_TEST)
    # finally reset viewport back to full window
    glViewport(0, 0, 1000, 800)


def check_collision(x, y, radius=player_size/2):
    """Check if a position (x, y) with given radius collides with any obstacle."""
    # Check boundary collisions
    if x - radius < -GRID_LENGTH or x + radius > GRID_LENGTH or y - radius < -GRID_LENGTH or y + radius > GRID_LENGTH:
        return True
    
    # Check obstacle collisions
    for ox, oy, width, height in obstacles:
        # Simple collision detection with rectangular obstacles
        if (x + radius > ox - width/2 and x - radius < ox + width/2 and
            y + radius > oy - height/2 and y - radius < oy + height/2):
            return True
    
    return False


def update_player():
    """Update player position and state."""
    global player_pos, collected_treasures, player_health, game_over, game_won
    
    if not game_active or game_over or game_won:
        return
    
    # Check for treasure collection
    for i, (tx, ty, collected) in enumerate(treasures):
        if not collected:
            # Distance check for treasure collection
            dx = player_pos[0] - tx
            dy = player_pos[1] - ty
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < player_size + 20:  # Player is close enough to treasure
                treasures[i][2] = True  # Mark as collected
                collected_treasures += 1
                
                # Check if all treasures are collected
                if collected_treasures >= TOTAL_TREASURES_NEEDED:
                    game_won = True
    
    # Check for monster collisions
    if not player_hidden:  # Only check when not in stealth mode
        for mx, my, _, _, _, _ in monsters:
            dx = player_pos[0] - mx
            dy = player_pos[1] - my
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < player_size + 25:  # Player is close to monster
                player_health -= 1  # Damage player
                
                # Game over if health depleted
                if player_health <= 0:
                    game_over = True
    
    # Time limit check
    if time.time() - start_time > total_time_limit:
        game_over = True


def update_monsters():
    """Update monster positions and patrol routes."""
    global monsters
    
    if not game_active or game_over or game_won:
        return
    
    for i, (mx, my, direction, speed, patrol_points, target_idx) in enumerate(monsters):
        # Get current target point
        tx, ty = patrol_points[target_idx]
        
        # Calculate direction to target
        dx = tx - mx
        dy = ty - my
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Update direction (angle) - convert to degrees
        if distance > 0:
            direction = math.degrees(math.atan2(dy, dx))
        
        # Check if monster is close to target
        if distance < 10:
            # Move to next patrol point
            target_idx = (target_idx + 1) % len(patrol_points)
        else:
            # Move towards the target
            mx += (dx / distance) * speed
            my += (dy / distance) * speed
        
        # Detect and avoid player if player isn't hidden
        if not player_hidden:
            pdx = player_pos[0] - mx
            pdy = player_pos[1] - my
            player_distance = math.sqrt(pdx*pdx + pdy*pdy)
            
            if player_distance < 200:
                # Monster detected player and chases
                chase_direction = math.degrees(math.atan2(pdy, pdx))
                direction = chase_direction
                
                # Move toward player faster
                mx += (pdx / player_distance) * speed * 1.5
                my += (pdy / player_distance) * speed * 1.5
                
                # Don't update target index - will resume patrol after losing player
        
        # Update monster position
        monsters[i] = [mx, my, direction, speed, patrol_points, target_idx]


def update_camera():
    """Update camera position based on player position and view mode."""
    global camera_pos
    
    if third_person_view:
        # Third-person view - camera follows player
        camera_x = player_pos[0] - camera_distance * math.cos(math.radians(player_angle))
        camera_y = player_pos[1] - camera_distance * math.sin(math.radians(player_angle))
        camera_z = player_pos[2] + camera_height
        camera_pos = (camera_x, camera_y, camera_z)
    else:
        # Fixed overhead view
        camera_pos = (0, 0, 800)


def setup_lighting():
    """Set up lighting for the 3D scene."""
    if light_enabled:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up ambient light
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient_light)
        
        # Set up positional light (simulates a torch/flashlight effect)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
        
        # Position light near player to simulate torch
        torch_x = player_pos[0] + 50 * math.cos(math.radians(player_angle))
        torch_y = player_pos[1] + 50 * math.sin(math.radians(player_angle))
        torch_z = player_pos[2] + 30
        light_pos = [torch_x, torch_y, torch_z, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    else:
        glDisable(GL_LIGHTING)


def setupCamera():
    """Configure the camera's projection and view settings."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.25, 0.1, 2000)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    x, y, z = camera_pos
    
    if third_person_view:
        # Third-person view - look at player
        gluLookAt(x, y, z,
                  player_pos[0], player_pos[1], player_pos[2],
                  0, 0, 1)
    else:
        # Top-down view - look at center of map
        gluLookAt(x, y, z,
                  0, 0, 0,
                  0, 1, 0)


def keyboardListener(key, x, y):
    """Handle keyboard inputs."""
    global player_pos, player_angle, player_hidden, game_active, third_person_view
    global game_over, game_won, light_enabled
    global boost_active, boost_start_time, last_boost_time

    
    # Get current key pressed
    k = key.lower()
    
    # Game restart
    if k == b'r':
        if game_over or game_won:
            init_game()
    
    # Game start
    if k == b' ' and not game_active and not game_over and not game_won:
        init_game()
    
    # Only process movement if game is active
    if not game_active or game_over or game_won:
        return
    
    # Calculate movement direction based on player angle
    move_speed = player_speed
    current_time = time.time()

    # If stealth, reduce base speed
    if player_hidden:
        move_speed *= 0.5

    # Check if Shift is held
    modifiers = glutGetModifiers()
    shift_held = modifiers & GLUT_ACTIVE_SHIFT

    # Trigger boost if Shift is held and cooldown is over
    if shift_held and not boost_active and current_time - last_boost_time >= boost_cooldown:
        boost_active = True
        boost_start_time = current_time
        last_boost_time = current_time

    # If boost is active, apply it
    if boost_active:
        if current_time - boost_start_time <= boost_duration:
            move_speed *= 2.0  # Boost multiplier
        else:
            boost_active = False  # End boost
    
    new_x, new_y = player_pos[0], player_pos[1]
    
    # Move forward (W key)
    if k == b'w':
        new_x += move_speed * math.cos(math.radians(player_angle))
        new_y += move_speed * math.sin(math.radians(player_angle))
        
    # Move backward (S key)
    if k == b's':
        new_x -= move_speed * math.cos(math.radians(player_angle))
        new_y -= move_speed * math.sin(math.radians(player_angle))
    
    # Strafe left (A key)
    if k == b'a':
        new_x -= move_speed * math.sin(math.radians(player_angle))
        new_y += move_speed * math.cos(math.radians(player_angle))

# Strafe right (D key)
    if k == b'd':
        new_x += move_speed * math.sin(math.radians(player_angle))
        new_y -= move_speed * math.cos(math.radians(player_angle))

    
    # Check for collisions before updating position
    if not check_collision(new_x, new_y):
        player_pos[0] = new_x
        player_pos[1] = new_y
    
    # Toggle stealth mode (C key)
    if k == b'c':
        player_hidden = not player_hidden
    
    # Toggle camera view (V key)
    if k == b'v':
        third_person_view = not third_person_view
    
    # Toggle light (L key)
    if k == b'l':
        light_enabled = not light_enabled


def specialKeyListener(key, x, y):
    """Handle special key inputs (arrow keys)."""
    global camera_height, camera_distance
    
    # Adjust camera height (UP/DOWN arrow keys)
    if key == GLUT_KEY_UP:
        camera_height += 10
    
    if key == GLUT_KEY_DOWN:
        camera_height = max(50, camera_height - 10)
    
    # Adjust camera distance (LEFT/RIGHT arrow keys)
    if key == GLUT_KEY_LEFT:
        camera_distance = max(100, camera_distance - 10)
    
    if key == GLUT_KEY_RIGHT:
        camera_distance += 10


def mouseListener(button, state, x, y):
    """Handle mouse inputs."""
    global third_person_view
    
    # Right mouse button toggles camera view
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        third_person_view = not third_person_view


def idle():
    """Idle function for continuous updates."""
    # Update game logic
    if game_active and not game_over and not game_won:
        update_player()
        update_monsters()
    
    # Update camera position
    update_camera()
    
    # Request display update
    glutPostRedisplay()


def showScreen():
    """Display function to render the game scene."""
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    setupCamera()
    setup_lighting()
    
    # Enable depth testing for 3D rendering
    glEnable(GL_DEPTH_TEST)
    
    # Enable blending for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw floor
    draw_floor()
    
    # Draw dungeon boundary walls
    draw_dungeon_boundary()
    
    # Draw obstacles (walls)
    for x, y, width, height in obstacles:
        draw_obstacle(x, y, width, height)
    
    # Draw treasures
    for x, y, collected in treasures:
        draw_treasure_chest(x, y, collected)
    
    # Draw monsters
    for x, y, direction, _, _, _ in monsters:
        draw_monster(x, y, direction)
    
    # Draw player
    draw_player()
    
    # Draw player status if game is active
    if game_active:
        draw_status_bar()
    
    # Draw 2D UI elements (time, score, messages)
    draw_game_ui()
    draw_topdown_minimap()
    
    # Swap buffers
    glutSwapBuffers()


def main():
    """Main function to set up OpenGL window and game loop."""
    # Initialize GLUT
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Dungeon Crawler")
    
    # Register callbacks
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    # Enable depth testing for 3D
    glEnable(GL_DEPTH_TEST)
    
    # Set clear color (dark for dungeon atmosphere)
    glClearColor(0.1, 0.1, 0.15, 1.0)
    
    # Enter main loop
    glutMainLoop()


if __name__ == "__main__":
    main()
