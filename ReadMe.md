# MicroVania

**A pixel-art boss battle where the real world influences the game.**

Micro Rouge is a Python/Pygame boss-fighting game developed for DurHack. It combines fast-paced platforming and combat with physical computing, using BBC micro:bits to bring real-world environmental data into the game.

Temperature, ambient light and physical movement influence the arena, turning the player's surroundings into part of the gameplay.

## Features

### ⚔️ Boss combat
- Fight a boss with distinct attack patterns and animations.
- Dodge attacks using movement, jumping, double jumping and dashing.
- Deal damage through close-range attacks.
- Manage health, damage immunity and knockback.
- Face increasingly challenging encounters as environmental conditions change.

### 🌍 A world influenced by the real one
Two BBC micro:bits work together to collect and transmit environmental data to the game.

| Sensor | In-game effect |
|---|---|
| Temperature | Changes the arena's weather and atmosphere. |
| Ambient light | Controls visibility, creating darker environments when light levels are low. |
| Accelerometer | Detects alternating tilts to trigger earthquake hazards. |

The sensor micro:bit collects environmental information and transmits it wirelessly to a receiver micro:bit. The receiver communicates with the computer over USB serial.

### 🎮 Pixel-art presentation
- Custom pixel-art visuals and animated sprites.
- Animated player and boss attacks.
- Custom interface, menus and gameplay transitions.
- Environmental visual effects integrated into the arena.

### 🤖 Dynamic boss dialogue
The project also integrates Gemini-powered boss dialogue, giving encounters more personality through dynamically generated taunts and dialogue.

## Tech Stack

- **Python** – Core game logic.
- **Pygame** – Rendering, input, animation and gameplay.
- **BBC micro:bit** – Environmental sensing and physical input.
- **Serial communication** – Transfers sensor readings to the game.
- **Gemini API** – Dynamic boss dialogue.
- **Git & GitHub** – Version control and collaboration.

## Getting Started

### Prerequisites

- Python 3.11 or later.
- Git.
- A Windows, macOS or Linux environment capable of running Pygame.

The game can be run without the micro:bit hardware if the project is configured to use its simulated/default sensor values.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/nasirr07/Durhack.git
   cd Durhack
   ```

2. Create a virtual environment:

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Launch the game from the project root:

   ```bash
   python -m game.main
   ```

## Hardware Setup

To use the physical sensor integration:

1. Flash the sensor micro:bit with the environmental data collection program.
2. Flash the receiver micro:bit with the wireless reception program.
3. Connect the receiver micro:bit to your computer over USB.
4. Ensure the game can access the receiver's serial port.
5. Launch the game.

When connected correctly, the game uses incoming sensor readings to influence the environment and trigger gameplay events.

## Controls

| Action | Input |
|---|---|
| Move | Movement keys |
| Jump / Double jump | Jump key |
| Dash | Left Shift |
| Attack | J |

*Check the in-game instructions for the current control layout.*

## Project Structure

```text
Durhack/
├── game/              # Core gameplay and game systems
├── assets/            # Sprites, backgrounds and audio
├── microbit_code/     # micro:bit programs and serial communication
├── tests/             # Automated tests
├── requirements.txt   # Python dependencies
└── README.md
```

## Development

Micro Rouge was built collaboratively during DurHack, with an emphasis on modular game architecture and integrating software with physical hardware.

The project uses Git for version control and Entire to capture AI-assisted development sessions and checkpoints.

## Team

Developed at **DurHack**.

---

*The world outside the screen doesn't have to stay outside the game.*
