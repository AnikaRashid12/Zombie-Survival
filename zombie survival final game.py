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
enemy_speed = 0.1   # slow speed for easier gameplay

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
lives = 5
game_over = False

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
    x = random.choice([-1,1]) * random.randint(200, 400)
    y = random.randint(-400, 400)
    if random.random() < 0.5:
        x, y = y, x
    return float(x), float(y)

def init_enemy():
    enemies.clear()
    for _ in range(enemy_num):
        ex, ey = rand_spawn_pos()
        enemies.append({
            "x": ex, "y": ey,
            "base_r": enemy_base_r,
            "phase": random.uniform(0, math.pi*2),
            "pulse": 0.0,
            "speed": enemy_speed
        })

def reset_games():
    global score, lives, bullets, game_over, person1
    player.update({"x":0, "y":0, "angle":0, "alive":True, "lie_down":False})
    bullets.clear()
    score = 0
    lives = 5
    init_enemy()
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
    # Body green
    glColor3f(0,1,0)
    glutSolidCube(enemy_base_r)
    # Head black
    glColor3f(0,0,0)
    glTranslatef(0,0,enemy_base_r/1.5)
    gluSphere(_quadric, enemy_base_r/2, 20, 20)
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

# ---------------- Game Logic ----------------
def update_bullets():
    global bullets
    for b in bullets[:]:
        rad=deg2rad(b["angle"])
        b["x"] += bull_speed*math.cos(rad)
        b["y"] += bull_speed*math.sin(rad)
        # Collision
        for e in enemies:
            if abs(e["x"]-b["x"])<enemy_base_r and abs(e["y"]-b["y"])<enemy_base_r:
                enemies.remove(e)
                if b in bullets: bullets.remove(b)
                break
        if b in bullets and abs(b["x"])>500 or abs(b["y"])>500:
            bullets.remove(b)

def update_enemies():
    global lives,game_over
    for e in enemies:
        blocked=False
        for t in trees:
            if abs(e['x']-t['x'])<t['size'] and abs(e['y']-t['y'])<t['size']:
                blocked=True
        if not blocked:
            dx, dy = player["x"]-e["x"], player["y"]-e["y"]
            dist = math.hypot(dx, dy)+1e-6
            e["x"] += enemy_speed*(dx/dist)
            e["y"] += enemy_speed*(dy/dist)
        if math.hypot(player["x"]-e["x"], player["y"]-e["y"])<enemy_base_r+20:
            lives-=1
            ex, ey = rand_spawn_pos()
            e["x"]=ex
            e["y"]=ey
        if lives<=0:
            trigger_game_over()


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
    global bull_cooldown
    if bull_cooldown>0: bull_cooldown-=1
    if not game_over:
        update_enemies()
        update_bullets()
    glutPostRedisplay()

def trigger_game_over():
    global game_over
    game_over=True
    player.update({"alive":False,"lie_down":True})

# ---------------- Display ----------------
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0,0,window_width,window_height)
    setupCamera()
    draw_danger_zone()
    draw_ground()
    for t in trees:
        draw_tree(t)
    for e in enemies:
        draw_enemy(e)
    for b in bullets:
        draw_bullet(b)
    draw_player()
    draw_text(10,770,f"Player Life: {lives}")
    draw_text(10,740,f"Score: {score}")
    if game_over:
        draw_text(400,400,"GAME OVER - Press R to Restart")
    glutSwapBuffers()

def main():
    random.seed(42)
    reset_games()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
    glutInitWindowSize(window_width,window_height)
    glutCreateWindow(b"Zombie Survival 3D")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__=="__main__":
    main()
