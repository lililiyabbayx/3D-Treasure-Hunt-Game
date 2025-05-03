# Dungeon Crawler

A 3D OpenGL-based dungeon crawler game where you must collect treasures while avoiding monsters in a limited time.

![Game Screenshot](screenshots/gameplay.png)

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Controls](#controls)
- [Gameplay Rules](#gameplay-rules)
- [Game Elements](#game-elements)
- [Tips & Strategies](#tips--strategies)

## Features

- **3D Environment**: Fully navigable 3D dungeon with walls and obstacles
- **Dynamic Lighting**: Torch-like lighting effect that follows the player
- **Smart Enemies**: Monsters with patrol routes that chase players when detected
- **Stealth Mechanics**: Hide from monsters using stealth mode
- **Speed Boost System**: Temporary speed enhancements with cooldown periods
- **Minimap**: Top-down minimap for better navigation
- **Multiple Camera Views**: Toggle between third-person and top-down perspectives
- **Time-based Challenge**: Complete objectives before the timer runs out
- **Visual Status Indicators**: Health bar and treasure collection status
- **Procedural Generation**: Random obstacle and treasure placement for replayability

![Features Overview](screenshots/features.png)

## Installation

1. Ensure you have Python installed on your system.
2. Install required dependencies:
   ```bash
   pip install PyOpenGL PyOpenGL_accelerate
   ```
3. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/dungeon-crawler.git
   ```
4. Run the game:
   ```bash
   python dungeon_crawler.py
   ```

## Controls

| Key           | Action                                           |
|---------------|--------------------------------------------------|
| W             | Move forward                                     |
| S             | Move backward                                    |
| A             | Strafe left                                      |
| D             | Strafe right                                     |
| C             | Toggle stealth mode                              |
| SHIFT         | Activate speed boost (when available)            |
| V             | Toggle camera view (third-person/top-down)       |
| L             | Toggle lighting effects                          |
| UP ARROW      | Increase camera height                           |
| DOWN ARROW    | Decrease camera height                           |
| LEFT ARROW    | Decrease camera distance                         |
| RIGHT ARROW   | Increase camera distance                         |
| RIGHT MOUSE   | Toggle camera view                               |
| SPACE         | Start game (at title screen)                     |
| R             | Restart game (after victory or defeat)           |

![Controls Guide](screenshots/controls.png)

## Gameplay Rules

1. **Objective**: Collect 5 treasure chests before the time limit (2 minutes) expires.
2. **Health**: Your health decreases when you come in contact with monsters.
3. **Game Over**: The game ends if your health reaches zero or time runs out.
4. **Victory**: Collect all 5 treasures to win the game.

### Time Management
- You have 120 seconds (2 minutes) to complete your objective
- The timer starts when the game begins
- Remaining time is displayed in the top left corner

### Health System
- You start with 100% health
- Health decreases when in contact with monsters
- Health bar changes color as health decreases:
  - Green: > 60%
  - Yellow: 30-60%
  - Red: < 30%

![Game Rules](screenshots/rules.png)

## Game Elements

### Player Character
- Blue sphere with red direction indicator
- Becomes translucent when in stealth mode
- Has status indicators showing health and treasure collected

### Monsters
- Red spheres with yellow eyes
- Follow preset patrol routes
- Chase the player when detected (unless player is in stealth mode)
- Cause damage on contact

### Treasures
- Gold-colored chests
- Occasionally emit a shining effect
- Turn brown when collected
- Need to collect 5 to win

### Environment
- Stone walls forming a dungeon
- Grid-patterned floor
- Outer boundary walls

![Game Elements](screenshots/elements.png)

## Special Abilities

### Stealth Mode
- Activated by pressing 'C'
- Makes player translucent and harder for monsters to detect
- Reduces movement speed by 50%
- Prevents monster detection
- Status indicated on screen when active

### Speed Boost
- Activated by holding SHIFT
- Doubles movement speed for 3 seconds
- Has a 9-second cooldown before it can be used again
- Status displayed on screen:
  - "Speed Boost: ACTIVE" - Currently in use
  - "Speed Boost: Cooldown (Xs)" - On cooldown
  - "Speed Boost: Ready" - Available for use

![Special Abilities](screenshots/abilities.png)

## Tips & Strategies

1. Use stealth mode to safely navigate past monsters and reach distant treasures.
2. Save your speed boost for emergency escapes or to quickly traverse open areas.
3. The minimap helps with navigation and spotting treasures/monsters at a distance.
4. Toggle camera views to get better perspectives in different situations.
5. Plan your route to efficiently collect all treasures within the time limit.
6. If monsters are close, consider using stealth rather than trying to outrun them.
7. Learn monster patrol patterns to time your movements accordingly.

## Development

This game is built using:
- Python
- PyOpenGL
- GLUT (OpenGL Utility Toolkit)




---

Enjoy the game! Feel free to report issues or contribute improvements.
