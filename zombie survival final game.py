from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# ---------------- Window Setup ----------------
window_width = 1000
window_height = 800

# ---------------- Player ----------------
player = {
    "x": 0.0,
    "y": 0.0,
    "angle": 0.0,
    "move_speed": 8.0,
    "rot_speed": 4.0,
    "alive": True,
    "lie_down": False
}

#----------------new----------------
danger_radius = 150      # Distance threshold
blink_state = False      # Toggles for blinking
blink_counter = 0


# ---------------- Bullets ----------------
bullets = []
bull_speed = 22
bull_cooldown = 0
bull_cooldown_frames = 8

# ---------------- Zombies ----------------
enemies = []
enemy_num = 5
enemy_base_r = 30
enemy_speed = 0.25   # slow speed for easier gameplay

# ---------------- Trees / Obstacles ----------------
trees = [{"x": -200, "y": -100, "size": 60}, {"x": 150, "y": 100, "size": 80}]

# ---------------- Camera ----------------
person1 = False
c_theta = 90
c_radius = 600
c_height = 400

# ---------------- Quadric ----------------
_quadric = None

# ---------------- Score / Game ----------------
score = 0
#----------------wave------------
wave = 1                   # Current wave number
wave_enemy_increment = 2   # How many more enemies per wave
wave_speed_increment = 0.05  # How much faster each wave
wave_cooldown = 0           # Frames until next wave starts
wave_cooldown_frames = 300  # 5 seconds at ~60fps

# ---------------- Health Pack & Game State ----------------
health_pack = 100  # [0..100]
game_over = False

# ---------------- Blood Trails ----------------
blood_trails = []
BLOOD_TTL_FRAMES = 240           # ~4 seconds at ~60fps
BLOOD_DETECT_RADIUS = 220        # zombies are attracted to nearby fresh blood
BLOOD_ATTRACT_WEIGHT = 0.45      # how strongly blood influences direction (0..1)
elapsed_time = 0.0

# ---------------- Helper Functions ----------------
def wrap_angle_deg(a):
    while a < -180:
        a += 360
    while a > 180:
        a -= 360
    return a

def deg2rad(a):
    return a * math.pi / 180.0

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def rand_spawn_pos(): 
    tile = 60
    grid_length = 1000
    grid_half = grid_length // tile
    half_ground = grid_half * tile
    margin = 250  # distance away from the walls

    side = random.choice(['top', 'bottom', 'left', 'right'])

    if side == 'top':
        x = random.uniform(-half_ground + margin, half_ground - margin)
        y = half_ground - margin
    elif side == 'bottom':
        x = random.uniform(-half_ground + margin, half_ground - margin)
        y = -half_ground + margin
    elif side == 'left':
        x = -half_ground + margin
        y = random.uniform(-half_ground + margin, half_ground - margin)
    else:  # right
        x = half_ground - margin
        y = random.uniform(-half_ground + margin, half_ground - margin)

    return float(x), float(y)

def init_enemy():
    enemies.clear()
    global enemy_num
    # Custom enemy counts for first three waves
    if wave == 1:
        current_enemy_count = 3  # Wave 1 easier
    elif wave == 2:
        current_enemy_count = 4  # Wave 2 slightly harder
    elif wave == 3:
        current_enemy_count = 6  # Wave 3 moderate
    else:
        current_enemy_count = enemy_num + (wave - 1) * wave_enemy_increment  # Normal scaling for later waves

    # Speed scales with wave 
    current_speed = enemy_speed + (wave - 1) * wave_speed_increment

    for _ in range(current_enemy_count):
        ex, ey = rand_spawn_pos()
        strength = random.randint(1, 3)
        enemies.append({
            "x": ex,
            "y": ey,
            "base_r": enemy_base_r,
            "phase": random.uniform(0, math.pi*2),
            "pulse": 0.0,
            "speed": current_speed,
            "strength": strength,
            "hit_cooldown": 0,
            "health": strength
        })


        
def reset_games():
    global score, health_pack, bullets, game_over, person1
    player.update({"x":0, "y":0, "angle":0, "alive":True, "lie_down":False})
    bullets.clear()
    score = 0
    health_pack=100
    init_enemy()
    init_treasures()
    game_over = False
    person1 = False

# ---------------- Drawing Functions ----------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_ground():
    grid_length = 1000
    tile = 60
    grid_half = grid_length // tile
    glBegin(GL_QUADS)
    for i in range(-grid_half, grid_half):
        for j in range(-grid_half, grid_half):
            if (i + j) % 2 == 0:
                glColor3f(0.36, 0.25, 0.20)   # coffee
            else:
                glColor3f(0.59, 0.29, 0.0)    # brown
            x0, y0 = i*tile, j*tile
            x1, y1 = x0 + tile, y0 + tile
            glVertex3f(x0, y0, 0)
            glVertex3f(x1, y0, 0)
            glVertex3f(x1, y1, 0)
            glVertex3f(x0, y1, 0)
    glEnd()

def draw_walls(): 
    wall_height = 100
    wall_thickness = 10
    tile = 60
    grid_length = 1000
    grid_half = grid_length // tile
    half_ground = grid_half * tile  # exact ground border

    glColor3f(0.5, 0.5, 0.5)  # gray walls

    # Top wall
    glPushMatrix()
    glTranslatef(0, half_ground - wall_thickness/2, wall_height/2)
    glScalef(2*half_ground + wall_thickness, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    # Bottom wall
    glPushMatrix()
    glTranslatef(0, -half_ground + wall_thickness/2, wall_height/2)
    glScalef(2*half_ground + wall_thickness, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    # Right wall
    glPushMatrix()
    glTranslatef(half_ground - wall_thickness/2, 0, wall_height/2)
    glScalef(wall_thickness, 2*half_ground + wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    # Left wall
    glPushMatrix()
    glTranslatef(-half_ground + wall_thickness/2, 0, wall_height/2)
    glScalef(wall_thickness, 2*half_ground + wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

def draw_tree(t):
    # Trunk
    glColor3f(0.55,0.27,0.07)
    glBegin(GL_QUADS)
    glVertex3f(t['x']-5, t['y']-15, 0)
    glVertex3f(t['x']+5, t['y']-15, 0)
    glVertex3f(t['x']+5, t['y'], 0)
    glVertex3f(t['x']-5, t['y'], 0)
    glEnd()
    # Leaves
    glColor3f(0,1,0)
    glPushMatrix()
    glTranslatef(t['x'], t['y'], 0)
    glutSolidSphere(t['size']/2, 20, 20)
    glPopMatrix()

def draw_bullet(b):
    glPushMatrix()
    glTranslatef(b["x"], b["y"], 12)
    glRotatef(b["angle"],0,0,1)
    glColor3f(1,1,0)
    glutSolidCube(10)
    glPopMatrix()

def draw_enemy(e): 
    global _quadric
    if not _quadric:
        _quadric = gluNewQuadric()
    glPushMatrix()
    glTranslatef(e["x"], e["y"], 0)

    # Determine color and scale by strength
    if e.get("strength", 1) == 1:      # light green
        glColor3f(0.5, 1.0, 0.5)
        scale = 1.0
    elif e["strength"] == 2:            # orange
        glColor3f(1.0, 0.65, 0.0)
        scale = 1.3
    else:                               # red
        glColor3f(1.0, 0.0, 0.0)
        scale = 1.6

    # Torso
    glPushMatrix()
    glScalef(1.0*scale, 0.6*scale, 1.5*scale)
    glutSolidCube(enemy_base_r)
    glPopMatrix()

    # Head
    glPushMatrix()
    glColor3f(0,0,0)
    glTranslatef(0, 0, 1.5*enemy_base_r*scale/2 + 10*scale)
    glutSolidSphere(10*scale, 16, 16)
    glPopMatrix()

    # Arms
    glColor3f(0.0,0.0,1.0)
    for dx in (-0.8*enemy_base_r*scale, 0.8*enemy_base_r*scale):
        glPushMatrix()
        glTranslatef(dx, 0, 0.5*enemy_base_r*scale)
        glScalef(0.3*scale,0.3*scale,1.0*scale)
        glutSolidCube(enemy_base_r)
        glPopMatrix()

    # Legs
    for dx in (-0.3*enemy_base_r*scale, 0.3*enemy_base_r*scale):
        glPushMatrix()
        glTranslatef(dx, 0, -0.75*enemy_base_r*scale)
        glScalef(0.4*scale,0.4*scale,1.0*scale)
        glutSolidCube(enemy_base_r)
        glPopMatrix()

    glPopMatrix()

def draw_player():
    global _quadric
    if not _quadric:
        _quadric=gluNewQuadric()
    glPushMatrix()
    glTranslatef(player["x"],player["y"],0)
    if player["lie_down"]:
        glRotatef(-90,0,1,0)
    glRotatef(player["angle"],0,0,1)
    # Body
    glColor3f(0,0.6,0)
    glutSolidCube(50)
    # Head
    glPushMatrix()
    glColor3f(0,0,0)
    glTranslatef(0,0,50)
    gluSphere(_quadric,20,20,20)
    glPopMatrix()
    # Legs
    glColor3f(0,0,1)
    for dx in (-15,15):
        glPushMatrix()
        glTranslatef(dx,-10,-30)
        glutSolidCube(20)
        glPopMatrix()
    # Arms
    glColor3f(1,0.8,0.6)
    for dx in (-30,30):
        glPushMatrix()
        glTranslatef(dx,0,25)
        glRotatef(90,0,1,0)
        gluCylinder(_quadric,6,6,30,12,12)
        glPopMatrix()
    # Gun
    glPushMatrix()
    glColor3f(0.7,0.7,0.7)
    glTranslatef(55,0,25)
    glScalef(2,0.5,0.5)
    glutSolidCube(30)
    glPopMatrix()
    glPopMatrix()

def create_blood_trail(px, py):
    """Spawn 3–4 red line segments around (px,py) that fade over time."""
    n = random.randint(3, 4)
    for _ in range(n):
        dx1 = random.uniform(-25, 25)
        dy1 = random.uniform(-25, 25)
        dx2 = dx1 + random.uniform(-30, 30)
        dy2 = dy1 + random.uniform(-30, 30)
        blood_trails.append({
            "x1": px + dx1,
            "y1": py + dy1,
            "x2": px + dx2,
            "y2": py + dy2,
            "ttl": BLOOD_TTL_FRAMES
        })

def update_blood_trails():
    for bt in blood_trails:
        bt["ttl"] -= 1
    # keep only alive trails
    alive = [bt for bt in blood_trails if bt["ttl"] > 0]
    blood_trails.clear()
    blood_trails.extend(alive)

def draw_blood_trails():
    if not blood_trails:
        return

    # No depth/blend/smooth state changes per template rules (#1, #2 not allowed)
    glLineWidth(3)  # allowed (#4)
    glBegin(GL_LINES)
    for bt in blood_trails:
        t = max(0.0, min(1.0, bt["ttl"] / BLOOD_TTL_FRAMES))  # 1 fresh → 0 old
        # fade by brightness only (no alpha)
        r = 0.9 * t + 0.1
        glColor3f(r, 0.0, 0.0)
        z = 2.0  # slight lift above ground so lines don’t z-fight
        glVertex3f(bt["x1"], bt["y1"], z)
        glVertex3f(bt["x2"], bt["y2"], z)
    glEnd()
    glLineWidth(1)


# ---------------- Treasure (as in your second code) ----------------
treasures = []

class Treasure:
    def __init__(self, x, y, z):
        self.pos = [x, y, z]
        self.size = 35
        self.rotation = 0
        self.float_offset = 0

    def update(self):
     self.rotation = (self.rotation + 1) % 360
     self.float_offset = 5 * math.sin(elapsed_time + self.pos[0]*0.1)

        
    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], self.pos[2] + self.float_offset)
        glRotatef(self.rotation, 0, 0, 1)
        glColor3f(1, 1, 0)
        glutSolidCube(self.size)
        glPopMatrix()

def init_treasures():
    treasures.clear()
    for _ in range(6):
        x, y = rand_spawn_pos()
        treasures.append(Treasure(x, y, 15))

def update_treasures():
    global score
    for t in treasures[:]:
        t.update()
        # Player pickup
        dist = math.hypot(player["x"] - t.pos[0], player["y"] - t.pos[1])
        if dist < 50:
            score += 10
            treasures.remove(t)

def draw_treasures():
    for t in treasures:
        t.draw()
# ---------------- Camera ----------------
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(120, window_width/window_height, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if person1:
        rad=deg2rad(player["angle"])
        cx=player["x"]-120*math.cos(rad)
        cy=player["y"]-120*math.sin(rad)
        cz=100
        lx=player["x"]+200*math.cos(rad)
        ly=player["y"]+200*math.sin(rad)
        gluLookAt(cx,cy,cz,lx,ly,40,0,0,1)
    else:
        rad=deg2rad(c_theta)
        cx=player["x"]+c_radius*math.cos(rad)
        cy=player["y"]+c_radius*math.sin(rad)
        cz=c_height
        gluLookAt(cx,cy,cz,player["x"],player["y"],20,0,0,1)

# ---------------- Input ----------------
def keyboardListener(key,x,y):
    global person1
    key = key.decode("utf-8")
    rad = deg2rad(player["angle"])  # convert angle once per keypress

    if key=='q':  # forward
        player["x"] += player["move_speed"]*math.cos(rad)
        player["y"] += player["move_speed"]*math.sin(rad)
    elif key=='e':  # backward
        player["x"] -= player["move_speed"]*math.cos(rad)
        player["y"] -= player["move_speed"]*math.sin(rad)
    elif key=='a':  # rotate left
        player["angle"] += player["rot_speed"]
    elif key=='d':  # rotate right
        player["angle"] -= player["rot_speed"]
    elif key=='s':  # strafe left
        player["x"] += player["move_speed"]*math.cos(rad + math.pi/2)
        player["y"] += player["move_speed"]*math.sin(rad + math.pi/2)
    elif key=='w':  # strafe right
        player["x"] += player["move_speed"]*math.cos(rad - math.pi/2)
        player["y"] += player["move_speed"]*math.sin(rad - math.pi/2)
    elif key==' ':  # fire
        fire_bullet()
    elif key in ('r','R') and game_over:  # restart
        reset_games()


def specialKeyListener(key,x,y):
    global c_theta,c_height
    if key==GLUT_KEY_UP:
        c_height = clamp(c_height+10, 150, 1200)
    elif key==GLUT_KEY_DOWN:
        c_height = clamp(c_height-10,150,1200)
    elif key==GLUT_KEY_LEFT:
        c_theta +=3
    elif key==GLUT_KEY_RIGHT:
        c_theta -=3

def mouseListener(btn,state,x,y):
    global person1
    if state != GLUT_DOWN: return
    if btn==GLUT_LEFT_BUTTON:
        fire_bullet()
    elif btn==GLUT_RIGHT_BUTTON:
        person1 = not person1

def fire_bullet():
    global bull_cooldown
    if bull_cooldown>0: return
    rad=deg2rad(player["angle"])
    bullets.append({"x":player["x"]+40*math.cos(rad),
                    "y":player["y"]+40*math.sin(rad),
                    "angle":player["angle"],"alive":True})
    bull_cooldown=bull_cooldown_frames

# ---------------- Gameplay Helpers ----------------
def set_background_by_health():
    """Blue (>40), Navy (<=40), Black (<=20)."""
    if health_pack <= 20:
        glClearColor(0.0, 0.0, 0.0, 1.0)       # black
    elif health_pack <= 40:
        glClearColor(0.0, 0.0, 0.5, 1.0)       # navy blue
    else:
        glClearColor(0.5, 0.8, 1.0, 1.0)       # blue sky

def trigger_game_over():
    global game_over
    game_over = True
    player.update({"alive": False, "lie_down": True})
# ---------------- Game Logic ----------------
def update_bullets(): 
    global bullets, score, enemies, health_pack
    # arena bounds matched to ground
    tile = 60
    grid_length = 1000
    half_ground = (grid_length // tile) * tile  # 960

    for b in bullets[:]:
        rad = deg2rad(b["angle"])
        b["x"] += bull_speed * math.cos(rad)
        b["y"] += bull_speed * math.sin(rad)

        hit = False
        for e in enemies:
            if e["health"] <= 0:
                continue

            # === AABB collision ===
            if abs(e["x"] - b["x"]) < enemy_base_r and abs(e["y"] - b["y"]) < enemy_base_r:
                e["health"] -= 1
                create_blood_trail(e["x"], e["y"])
                hit = True

                # killed?
                if e["health"] <= 0:
                    strength = e.get("strength", 1)
                    score += {1: 1, 2: 2, 3: 3}.get(strength, 1)

                    # Heal on kill: +20, cap 100
                    if health_pack < 100:
                        health_pack = min(100, health_pack + 20)

                break  # stop checking other enemies for this bullet

        if hit:
            bullets.remove(b)
            continue

        # Despawn outside arena with margin
        if abs(b["x"]) > (half_ground + 40) or abs(b["y"]) > (half_ground + 40):
            bullets.remove(b)

def update_enemies():
    global health_pack, wave, wave_cooldown, game_over

    # Keep only alive enemies
    alive_enemies_list = [e for e in enemies if e["health"] > 0]
    alive_enemies = len(alive_enemies_list)

    for e in alive_enemies_list:
        # Decrement hit cooldown
        if e.get("hit_cooldown", 0) > 0:
            e["hit_cooldown"] -= 1

        # Blood attraction
        target_blood = None
        best_ttl = -1
        ex, ey = e["x"], e["y"]
        for bt in blood_trails:
            mx = 0.5*(bt["x1"] + bt["x2"])
            my = 0.5*(bt["y1"] + bt["y2"])
            if math.hypot(mx - ex, my - ey) <= BLOOD_DETECT_RADIUS:
                if bt["ttl"] > best_ttl:
                    best_ttl = bt["ttl"]
                    target_blood = (mx, my)

        # Move towards player (blend blood)
        dx = player["x"] - e["x"]
        dy = player["y"] - e["y"]
        dist_p = math.hypot(dx, dy) + 1e-6
        vx = dx / dist_p
        vy = dy / dist_p

        if target_blood:
            bx = target_blood[0] - e["x"]
            by = target_blood[1] - e["y"]
            dist_b = math.hypot(bx, by) + 1e-6
            bvx = bx / dist_b
            bvy = by / dist_b
            w = BLOOD_ATTRACT_WEIGHT
            vx = (1 - w) * vx + w * bvx
            vy = (1 - w) * vy + w * bvy
            vlen = math.hypot(vx, vy) + 1e-6
            vx /= vlen
            vy /= vlen

        # Check tree blocking
        is_blocked = any(abs(e['x']-t['x']) < t['size'] and abs(e['y']-t['y']) < t['size'] for t in trees)
        if not is_blocked:
            e["x"] += e["speed"] * vx
            e["y"] += e["speed"] * vy

        # Attack player
        if math.hypot(player["x"] - e["x"], player["y"] - e["y"]) < (enemy_base_r + 20) and e.get("hit_cooldown",0) == 0:
            health_pack = max(0, health_pack - 20)
            create_blood_trail(player["x"], player["y"])
            e["hit_cooldown"] = 50

    # Update global enemies list to only alive ones
    enemies[:] = alive_enemies_list

    # --- Wave management ---
    if alive_enemies == 0 and not game_over:
        if wave_cooldown == 0:
            wave += 1
            wave_cooldown = wave_cooldown_frames  # 5 sec
        else:
            wave_cooldown -= 1
            if wave_cooldown == 0:
                init_enemy()

def draw_danger_zone():
    global blink_state, blink_counter
    # Check if any zombie is close
    close = any(math.hypot(e["x"]-player["x"], e["y"]-player["y"]) < danger_radius
                for e in enemies)
    if not close: 
        return  # invisible if no zombies nearby

    # Blink effect toggle
    blink_counter += 1
    if blink_counter % 20 == 0:  # Toggle every ~20 frames
        blink_state = not blink_state
    if not blink_state:
        return  # Skip drawing half the time

    # Draw circle on ground
    glColor3f(1, 0, 0)  # red
    glBegin(GL_LINE_LOOP)
    for i in range(60):
        ang = 2*math.pi*i/60
        glVertex3f(player["x"] + danger_radius*math.cos(ang),
                   player["y"] + danger_radius*math.sin(ang), 1)
    glEnd()


def idle():
    global bull_cooldown, elapsed_time, wave_cooldown
    # set background by health each frame (day/night)
    set_background_by_health()

    # advance simple time ( ~60 fps )
    elapsed_time += 0.016

    # decrement bullet cooldown
    if bull_cooldown > 0:
        bull_cooldown -= 1

    # ---------------- Wave cooldown ----------------
    if wave_cooldown > 0:
        wave_cooldown -= 1
        if wave_cooldown == 0:
            init_enemy()  # spawn next wave

    if not game_over:
        update_enemies()
        update_bullets()
        update_blood_trails()
        update_treasures()
    glutPostRedisplay()


    
def draw_health_battery():
    """Top-right 'battery' for health: green, turns red at <=20 and shows 'Low health'."""
    # Battery geometry
    body_w, body_h = 180, 28
    cap_w = 8
    pad = 3
    x = window_width - 20 - body_w - cap_w   # right margin 20px
    y = window_height - 35                   # top margin ~35px

    # 2D overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Outline (white)
    glColor3f(1, 1, 1)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + body_w, y)
    glVertex2f(x + body_w, y + body_h)
    glVertex2f(x, y + body_h)
    glEnd()

    # Battery cap (solid white)
    glBegin(GL_QUADS)
    glVertex2f(x + body_w,           y + body_h * 0.25)
    glVertex2f(x + body_w + cap_w,   y + body_h * 0.25)
    glVertex2f(x + body_w + cap_w,   y + body_h * 0.75)
    glVertex2f(x + body_w,           y + body_h * 0.75)
    glEnd()

    # Fill bar
    frac = max(0.0, min(1.0, health_pack / 100.0))
    if health_pack <= 20:
        glColor3f(0.9, 0.1, 0.1)   # red
    else:
        glColor3f(0.1, 0.85, 0.2)  # green

    fill_w = (body_w - 2 * pad) * frac
    glBegin(GL_QUADS)
    glVertex2f(x + pad,        y + pad)
    glVertex2f(x + pad + fill_w, y + pad)
    glVertex2f(x + pad + fill_w, y + body_h - pad)
    glVertex2f(x + pad,        y + body_h - pad)
    glEnd()

    glLineWidth(1)

    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # Low health label
    if health_pack <= 20:
        # place it just to the left of the battery
        draw_text(x - 90, y + 5, "Low health")

# ---------------- Display ----------------
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0,0,window_width,window_height)
    setupCamera()
    draw_danger_zone()
    draw_ground()
    draw_walls()
    for t in trees:
        draw_tree(t)
    draw_blood_trails()
    draw_treasures()
    for e in enemies:
        draw_enemy(e)
    for b in bullets:
        draw_bullet(b)
    draw_player()
    draw_player()
    # HUD
    draw_text(10, window_height - 30, f"Health Pack: {health_pack}")
    draw_text(10, window_height - 55, f"Score: {score}")
    draw_health_battery()
    if game_over:
        draw_text(window_width/2 - 120, window_height/2, "GAME OVER - Press R to Restart")
    draw_text(10, window_height - 80, f"Wave: {wave}")

    glutSwapBuffers()
# ---------------- Reshape (nice to have) ----------------
def reshape(w, h):
    global window_width, window_height
    window_width = max(1, w)
    window_height = max(1, h)
    glViewport(0, 0, window_width, window_height)
    
def main():
    random.seed(42)
    reset_games()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
    glutInitWindowSize(window_width,window_height)
    glutCreateWindow(b"Zombie Survival 3D")
    glEnable(GL_DEPTH_TEST)
    
     # initial sky; will be overridden each frame by set_background_by_health()
    glClearColor(0.5, 0.8, 1.0, 1.0)
    
    glutDisplayFunc(showScreen)
    glutReshapeFunc(reshape)
   
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__=="__main__":
    main()
