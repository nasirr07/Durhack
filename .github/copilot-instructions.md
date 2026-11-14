# Copilot Instructions

## Project Overview

We are developing **MicroRogue**, a 2D roguelite boss-fighting game built with Python and Pygame.

The game integrates two BBC micro:bits to collect real-world environmental data and influence gameplay dynamically.

The three primary sensor inputs are:

- Temperature
- Ambient light
- Tilt / accelerometer data

The project should prioritise a responsive gameplay experience, clean architecture and reliable hardware communication.

## Core Architecture

The application consists of three main components:

### 1. Sensor micro:bit

- Collect temperature, ambient light and accelerometer readings.
- Transmit sensor readings wirelessly to the receiver micro:bit.
- Keep sensor sampling and transmission logic separate from game logic.

### 2. Receiver micro:bit

- Receive sensor readings from the sensor micro:bit using radio communication.
- Forward the readings to the laptop through USB serial communication.
- Ensure messages use a consistent, structured format.

### 3. Pygame application

- Read incoming sensor data from the receiver micro:bit.
- Convert raw sensor readings into meaningful gameplay effects.
- Update boss behaviour, arena conditions and visual effects.
- Keep sensor communication independent of the main game loop.

## Gameplay Requirements

The three sensor inputs should have meaningful and distinguishable effects.

### Temperature

High temperatures should influence the boss and arena through:

- Fire-based visual effects.
- Fire-based boss attacks or abilities.
- Changes to the arena landscape, such as scorching or environmental hazards.

### Ambient Light

Low ambient light should:

- Reduce the player's visibility.
- Create a dynamic visibility or darkness effect.
- Influence how the player navigates and responds to boss attacks.

### Tilt / Accelerometer

Physical movement or changes in orientation should trigger:

- Earthquake effects.
- Arena disruption.
- Changes to the arena's orientation or apparent tilt.

Gameplay effects should respond to sensor changes without making the game unfair or unplayable.

## Technical Guidelines

### Python and Pygame

- Use Python for the game application.
- Use Pygame for rendering, input handling, game logic and audio.
- Keep the game loop responsive and avoid blocking operations.
- Avoid performing serial reads that can freeze or stall rendering.
- Separate rendering, input handling, gameplay logic and sensor processing.
- Prefer small, reusable functions and classes with clear responsibilities.

### Hardware Communication

- Use a clearly defined message format between the micro:bits and the laptop.
- Validate incoming sensor readings before using them.
- Handle missing, malformed or delayed sensor data gracefully.
- Avoid assuming that sensor readings are always available.
- Keep hardware communication separate from gameplay logic.
- Provide a simulated sensor-data mode so the game can be developed and tested without physical micro:bits.

### Sensor Processing

- Map raw sensor readings to meaningful gameplay values.
- Use configurable thresholds rather than scattering arbitrary numbers throughout the codebase.
- Consider smoothing or filtering noisy sensor readings.
- Prevent sudden sensor fluctuations from causing unstable gameplay.
- Ensure sensor effects can be tested independently of the hardware.

## Development Principles

1. **Understand before implementing.** Inspect the existing codebase and understand its architecture before making changes.
2. **Plan significant changes.** For larger features, explain the proposed approach and affected components before implementation.
3. **Keep changes focused.** Avoid unnecessary refactoring or modifying unrelated files.
4. **Avoid overengineering.** This is a hackathon project. Prioritise working, demonstrable features over unnecessary abstractions.
5. **Preserve existing functionality.** Do not remove working features unless explicitly requested.
6. **Explain technical decisions.** Briefly explain important implementation choices and trade-offs.
7. **Test changes.** Verify functionality where possible and report anything that could not be tested.

## Working With the Team

- Do not overwrite or revert another team member's work.
- Inspect Git status and existing changes before modifying files.
- Avoid committing, pushing or modifying Git history unless explicitly instructed.
- Do not commit secrets, credentials or private configuration.
- Keep documentation updated when changing important architecture or setup decisions.
- Prefer readable, maintainable code over unnecessarily clever implementations.

## Hackathon Priorities

The project has limited development time. Prioritise in this order:

1. A playable Pygame boss fight.
2. Reliable communication between the two micro:bits.
3. Working sensor-to-gameplay integration.
4. Clear and noticeable environmental effects.
5. Polish, visual effects and additional gameplay features.

A complete, stable core experience is more important than an unfinished collection of ambitious features.

## AI Agent Behaviour

- Act as a collaborative software engineering assistant, not an autonomous code generator.
- Explain unfamiliar concepts when they are relevant to implementation.
- Do not generate large amounts of code without first establishing the intended design.
- Ask for clarification when requirements are genuinely ambiguous.
- Prefer incremental implementation so team members can understand, review and debug changes.
- Highlight hardware dependencies and assumptions explicitly.
- Never claim that hardware functionality has been tested unless it has actually been tested.