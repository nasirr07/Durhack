# Copilot Instructions

## Project overview

MicroRogue is a Python/Pygame 2D boss-fighting game whose intended gameplay is influenced by temperature, ambient light, and tilt data from BBC micro:bits. The repository also contains a separate UI prototype and art assets.

## Codebase Exploration with Entire Graph

Use Entire Graph for code discovery, structural understanding and semantic change analysis.

### Rules
- Before locating or modifying code, query Entire Graph first.
- Use Graph whenever investigating definitions, callers, dependencies or references.
- Do not rely on grep or file searches for structural code discovery.
- Use direct source inspection to verify relevant implementation details before editing.
- Use Graph impact analysis before making changes that could affect other components.
- Identify relevant tests and run focused tests after making changes.
- Prefer the smallest complete change and avoid unnecessary refactoring.

### Commands

Run these from the repository root:

```powershell
entire graph query --repo . --profile full --head --format agent --max-context-bytes 4096 --query "<task>"
entire graph def --repo . --head --max-context-bytes 4096 <Name>
entire graph neighbors --repo . --head --format agent --max-context-bytes 4096 --symbol <Name> --direction in
entire graph impact --repo . --head --max-context-bytes 4096 --symbol <Name>
```

Use `--head` for committed code. Omit it when investigating uncommitted working-tree changes.

Use grep/rg only for literal strings, configuration keys, environment variables and filenames.

Refer to `AGENTS.md` and `.entire/agent-guide.md` for the complete Entire Graph operating instructions.

Never assume Graph results are complete or that an empty relationship result proves no dependency exists. Verify against source code where necessary.


## Commands

Run commands from the repository root unless noted otherwise.

### Game and tests

The game modules use top-level imports and are intended to run with `game` as the working directory:

```text
cd game
python main.py
```

The game starts fullscreen and expects a connected receiver micro:bit. `SerialReader` searches for a device with USB VID `3368` and PID `516`; without that device, the live game may not receive sensor data.

Run all gameplay tests:

```text
python -m unittest discover -s game -p "test*.py"
```

Run one test:

```text
cd game
python -m unittest test_gameplay.GameplayTests.test_name
```

Run a syntax/bytecode check for the game modules:

```text
python -m compileall -q game
```

`install-libraries.bat` installs the MicroPython helper packages used for micro:bit development:

```text
install-libraries.bat
```

There is no repository-configured build system or lint command. Do not invent a package entry point or assume the `ui code` prototype is part of the current game launch path.

## Architecture

### Pygame game

- `game/main.py` owns initialization, the fullscreen window, the frame loop, event polling, update order, collision/damage orchestration, rendering, and serial-data display.
- `game/player.py` owns player state: input buffering, coyote time, jumping, gravity, movement, dash timers, attacks, damage immunity, knockback, and the player hit/attack rectangles. `Player.update(dt, ...)` advances simulation using seconds-based delta time.
- `game/boss.py` currently provides the boss rectangle, gravity/floor behavior, health, and rendering.
- `game/collision.py` contains reusable rectangle checks plus player floor/screen-boundary resolution and player-boss overlap resolution. Boss collision is resolved after entity updates and records contact-edge/direction state on the player.
- `game/combat.py` checks the player's active attack rectangle against the boss and uses `player.attack_id` so one attack swing damages the boss once.
- `game/reader.py` runs serial reading on a daemon thread, parses JSON lines, and exposes the latest values through a shared dictionary. The main loop reads that dictionary without blocking on serial I/O.
- The current frame order is: input/events, player update, boss update, player-boss collision and damage, combat attack resolution, then drawing.

### Hardware data path

The intended path is:

1. `microbit-code/controller/main.py` samples temperature, light, and accelerometer X direction.
2. The controller sends a comma-separated radio message on channel 10, group 200.
3. `microbit-code/receiver/main.py` receives the message and prints JSON over USB serial.
4. `game/reader.py` finds the receiver by VID/PID and updates the game's latest sensor dictionary.

The serial JSON keys are `temp`, `light`, and `dir`. Preserve this shape when changing the hardware/game boundary. `microbit-code/serial_reader` is a separate micro:bit serial-output utility and is not the same as the desktop game's `game/reader.py`.

### UI prototype

`ui code/` contains an additional screen/widget framework with start, controls, settings, and save-selection screens. It is separate from the current `game/main.py` entry point; changes to it should not be assumed to affect the playable Pygame loop.

## Repository-specific conventions

- Keep the game as flat top-level modules. Existing imports such as `from player import Player` assume execution from `game`, rather than package-qualified imports from the repository root.
- Use `dt` in seconds for timers, movement, gravity, dash duration, cooldowns, and knockback decay. The main loop caps `dt` at `0.05`.
- Store world positions as floats and construct `pygame.Rect` values from rounded positions for collision and drawing.
- Countdown timers are reduced with `max(0, timer - dt)`. Preserve separate timers for distinct behaviors; damage immunity must not implicitly control knockback or other movement effects.
- Keep collision resolution and gameplay response separate: collision helpers correct overlap/boundaries and expose collision state, while `main.py` decides when a collision causes damage.
- Preserve the attack ID convention: increment `Player.attack_id` when a new attack starts, and let `CombatSystem.last_hit_attack_id` prevent multiple hits from one swing.
- Keep serial parsing off the Pygame frame loop. Validate/ignore malformed JSON without blocking rendering, and preserve the latest known sensor values when a message omits a key.
- Micro:bit radio settings are shared between controller and receiver; changing channel/group or message formatting requires updating both ends and the desktop parser.
- Inspect `git status` and existing changes before editing. The repository includes generated/session metadata and large art assets; do not modify or commit those as part of unrelated gameplay work.
- For repository workflow and source-discovery requirements, consult `.entire/agent-guide.md`; `AGENTS.md` and `CLAUDE.md` point to that guide.
- Preserve the existing hardware-independent unit-test path. Tests import game modules as top-level modules, so run them with the commands above rather than changing imports just to run from the repository root.
