A 2D roguelite boss-fighting game where the physical environment influences the virtual world.

Overview

MicroRogue is a Python/Pygame 2D roguelite in which the player faces a boss inside a dynamic arena. Unlike a traditional boss fight, the game world responds to real-world environmental conditions measured by two BBC micro:bits.

Temperature, ambient light and physical movement influence the boss's abilities, live AI dialogue, and the arena itself, creating an unpredictable experience where the player's surroundings become part of the challenge.

The environment is the enemy.

Core Gameplay

The player must survive and defeat a boss whose behaviour, attacks, and surrounding arena change in response to live sensor data:

- Temperature (High temperature >= 26°C): Boss enters fire mode, launching 5-fireball volleys and summoning scorching heatwaves across the arena.
- Temperature (Normal temperature): Boss casts orange incantation circles and fires timed laser beams when the player is at range.
- Light (Low ambient light): Visibility dynamically decreases with the micro:bit light sensor, restricting how much of the arena the player can see.
- Tilt (Physical movement or orientation changes): Triggers earthquakes, screen rumbling, environmental disruption, and reactive boss taunts.
- Live AI Boss Taunts (Gemini API): A Pokémon-style dialogue system at the bottom of the screen generates real-time, context-aware boss taunts reacting to temperature, darkness, earthquakes, and player health.

Hardware Architecture

The project uses two BBC micro:bits to collect and transmit environmental data:

- Sensor micro:bit: Measures temperature, ambient light and tilt using its onboard sensors and broadcasts JSON packets over radio.
- Receiver micro:bit: Receives the sensor readings wirelessly from the first micro:bit and streams them to the laptop over USB serial.
- Game application: A multi-threaded Python/Pygame application reads the incoming serial data without blocking the 60 FPS game loop and translates it into live gameplay changes.

Technology Stack

- Python – Core game logic, threaded serial reader, and application architecture.
- Pygame – 2D rendering, sprite sheet animation engine, lighting overlays, audio, and combat physics.
- Google Gemini API – Real-time contextual boss dialogue and environmental taunts.
- BBC micro:bit & MicroPython – Environmental sensing and wireless radio telemetry.
- Serial communication (pyserial) – Low-latency sensor streaming from the receiver micro:bit to the laptop.
- Git & GitHub – Version control and collaboration.
- Entire – Captures AI-assisted development sessions, prompts, and checkpoints.

Key Features

- 2D roguelite boss encounter with custom SpriteSheet and Animator system.
- Real-world temperature switches boss between laser incantations and fireball/heatwave attacks.
- Ambient light dynamically scales arena darkness and visibility.
- Physical tilt triggers earthquakes, screen shake, and reactive dialogue.
- Live Gemini AI boss taunts presented in a retro Pokémon-style dialogue box with audio blips.
- Wireless radio communication between two BBC micro:bits.
