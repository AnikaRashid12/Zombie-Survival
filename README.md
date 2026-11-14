# 🧟 Zombie Survival 3D

**Zombie Survival 3D** is a 3D zombie shooter survival game developed using **Python, OpenGL, GLUT, and GLU**. The player must survive multiple waves of zombies, collect treasures, avoid enemy attacks, and defeat a powerful Boss Zombie to win the game.

The game features a 3D arena, enemy AI, shooting mechanics, health management, dynamic difficulty, and interactive camera controls.

---

## 🎮 Game Overview

The player starts in a 3D survival arena surrounded by zombies approaching from different directions. Each zombie has different strength and health levels. As the player progresses through the waves, enemies become faster and more challenging.

After surviving the first three waves, the player faces a powerful Boss Zombie. Defeating the boss is the ultimate objective.

## ✨ Features

### 1. 3D Survival Environment
- Coffee and brown checkerboard arena.
- 3D boundary walls surrounding the playing area.
- Trees and obstacles placed throughout the arena.
- Third-person and first-person camera views.

### 2. Zombie AI and Enemy System
- Zombies spawn randomly from the edges of the arena.
- Enemies automatically chase the player.
- Three zombie strength levels with different sizes and appearances.
- Zombies can follow blood trails instead of directly approaching the player.
- Enemy movement includes obstacle detection and basic detour behavior.
- Zombie attacks reduce player health.

### 3. Shooting Mechanics
- Shoot zombies using keyboard or mouse controls.
- Bullets travel in the direction the player is facing.
- Shooting cooldown prevents continuous firing.
- Zombies require different numbers of hits depending on their strength.
- Defeating zombies increases the player's score.

### 4. Wave-Based Difficulty System
- **Wave 1:** 3 zombies.
- **Wave 2:** 4 zombies.
- **Wave 3:** 6 zombies.
- Zombie speed increases with each wave.
- A short cooldown occurs between waves.
- After completing Wave 3, the Boss Zombie appears.

### 5. Boss Zombie
- A large and powerful zombie appears after the third wave.
- The boss has a separate health bar.
- It moves faster than normal zombies.
- Boss attacks cause significant damage to the player.
- The player must land multiple shots to reduce its health.
- Defeating the boss results in victory.

### 6. Treasure Collection
- Six treasures spawn at random positions.
- Treasures rotate and float above the ground.
- Collecting a treasure rewards the player with 10 points.

### 7. Health and Survival System
- Player starts with 100 health points.
- Normal zombie attacks reduce health by 20 points.
- Boss attacks reduce health by 40 points.
- Defeating normal zombies restores 20 health points, up to the maximum of 100.
- Health is displayed through a visual battery indicator.
- The background changes according to the player's health.
- A low-health warning appears when health reaches 20 or below.

### 8. Additional Visual Effects
- Blood trails appear when zombies or the player are hit.
- Blood trails gradually fade over time.
- Nearby zombies trigger a blinking red danger-zone indicator around the player.
- Different zombie types have distinct colors and sizes.

### 9. Game State Management
- Real-time score and wave tracking.
- Player victory and defeat conditions.
- Game-over screen displaying the final score.
- Restart functionality.

---

## 🕹️ Controls

| Key / Button | Action |
|---|---|
| `Q` | Move forward |
| `E` | Move backward |
| `A` | Rotate left |
| `D` | Rotate right |
| `S` | Strafe left |
| `W` | Strafe right |
| `SPACE` | Shoot bullets |
| `Left Mouse Button` | Shoot bullets |
| `Right Mouse Button` | Toggle first-person / third-person view |
| `UP Arrow` | Move camera higher |
| `DOWN Arrow` | Move camera lower |
| `LEFT Arrow` | Rotate camera left |
| `RIGHT Arrow` | Rotate camera right |
| `R` | Restart after game over |

---

## 🛠️ Technologies Used

- **Python** – Core programming language.
- **PyOpenGL** – 3D graphics rendering.
- **GLUT** – Window management, keyboard and mouse input, and game loop.
- **GLU** – Camera positioning and 3D geometric rendering.
- **Math** – Distance calculations, movement, collision detection, and enemy AI.
- **Random** – Randomized zombie and treasure spawning.

---

## ⚙️ Installation and Setup

### Prerequisites
- Python 3.x
- pip
- OpenGL-compatible graphics environment

### Step 1: Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
```

### Step 2: Navigate to the Project Directory

```bash
cd YOUR_PROJECT_FOLDER
```

### Step 3: Install Required Libraries

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

### Step 4: Run the Game

```bash
python main.py
```

*Replace `main.py` with the actual name of your Python file if different.*

---

## 🏆 Objective

Survive all three zombie waves, collect treasures to increase your score, manage your health, and defeat the final Boss Zombie.

**Can you survive the apocalypse?**

---

## 👩‍💻 Project Information

**Project Name:** Zombie Survival 3D  
**Category:** 3D Shooter / Survival Game  
**Graphics Library:** OpenGL  
**Language:** Python

Developed as part of an academic Computer Graphics project.

---

*Survive the waves. Collect the treasures. Defeat the boss. Stay alive!* 🧟‍♂️
