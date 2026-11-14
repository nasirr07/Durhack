A 2D roguelite boss-fighting game where the physical environment influences the virtual world.

Overview

MicroRogue is a Python/Pygame 2D roguelite in which the player faces a boss inside a dynamic arena. Unlike a traditional boss fight, the game world responds to real-world environmental conditions measured by two BBC micro.

Temperature, ambient light and physical movement influence the boss's abilities and the arena itself, creating an unpredictable experience where the player's surroundings become part of the challenge.

The environment is the enemy.

Core Gameplay

The player must survive and defeat a boss whose behaviour and the surrounding arena change in response to live sensor data.

Sensor

Environmental condition

In-game effect

Temperature

High temperature

Boss gains fire effects and fire-based attacks. The arena landscape may become scorched or change dynamically.

Light

Low ambient light

Visibility decreases, restricting how much of the arena the player can see.

Tilt

Physical movement or orientation changes

Triggers earthquakes, environmental disruption or tilting of the arena.

These effects are designed to make each encounter feel different and force the player to adapt to changing conditions.

Hardware Architecture

The project uses two BBC micro to collect and transmit environmental data.

Sensor micro:bit: Measures temperature, ambient light and tilt using its onboard sensors.

Receiver micro:bit: Receives the sensor readings wirelessly from the first micro and communicates them to the laptop over USB.

Game application: A Python/Pygame application reads the incoming sensor data and translates it into changes in gameplay.



Technology Stack

Python – Core game logic and application.

Pygame – 2D rendering, game loop, input handling and gameplay.

BBC micro – Environmental sensing and wireless communication.

MicroPython – Micro programming.

Serial communication – Transfers sensor readings from the receiver micro to the laptop.

Git & GitHub – Version control and collaboration.

Entire – Captures AI-assisted development sessions and checkpoints.


Key Features

2D roguelite boss encounter.

Real-world temperature influences boss abilities and arena effects.

Ambient light dynamically affects player visibility.

Physical tilt triggers earthquakes and arena disturbances.

Wireless communication between two micro.

Real-time interaction between physical sensor data and virtual gameplay.


Project Status

Currently in development as part of a hackathon project.