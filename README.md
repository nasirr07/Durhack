# MicroRogue

MicroRogue is a Python/Pygame boss-fighting game where temperature, ambient light, and physical movement shape the virtual arena. It combines a playable 2D combat loop with a two-micro:bit sensor pipeline.

> **The environment is the enemy.**

## Why this project is interesting

- **Temperature:** switches the boss between fire attacks and normal-mode abilities.
- **Ambient light:** changes the player's visibility.
- **Tilt:** triggers earthquakes, screen shake, and environmental disruption.
- **Hardware integration:** a sensor micro:bit broadcasts readings to a receiver micro:bit, which forwards JSON over USB serial.
- **Maintainable core:** gameplay is split into player, boss, collision, combat, hazards, lighting, audio, and session modules with focused unit tests.

## Technology

- Python 3.11+ and Pygame
- pyserial for non-blocking receiver communication
- BBC micro:bit and MicroPython radio firmware
- Standard-library HTTP integration for optional boss taunts

## Quick start

### 1. Install dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Run the test suite

```powershell
python -m unittest discover -s game -p "test*.py"
python -m compileall -q game
```

The compile check is currently the reliable baseline check. The existing unittest files include older `Boss` API expectations and need a separate test migration before they can be used as a required CI gate.

### 3. Launch the game

The game modules use flat imports, so run the entry point from the `game` directory:

```powershell
Set-Location game
python main.py
```

The game can start without a connected receiver; sensor-driven features use the latest available readings. A receiver micro:bit is required for live temperature, light, and tilt input.

## Controls

The current playable build uses keyboard controls for movement, jumping, attacks, and dashing. The exact bindings are defined in `game/player.py` and should be checked in-game because they may evolve with the prototype.

## Hardware data path

```text
sensor micro:bit
    -> radio channel 10 / group 200
receiver micro:bit
    -> USB serial at 115200 baud
game/reader.py
    -> game/session.py and gameplay systems
```

The desktop boundary preserves the sensor keys `temp`, `light`, and `dir`. Firmware lives in `microbit-code/`:

- `controller/` samples and broadcasts sensor values.
- `receiver/` receives radio messages and prints JSON.
- `serial_reader/` contains the separate micro:bit serial-output utility.

## Repository map

| Path | Purpose |
| --- | --- |
| `game/` | Current playable Pygame application and unit tests |
| `assets/` | Sprites, maps, fonts, and audio used by the game |
| `microbit-code/` | Controller, receiver, and serial utility firmware |
| `ui code/` | Earlier standalone UI prototype; not the current launch path |
| `Specs.md` | Historical hackathon checklist |

## Development notes

- Run tests from the repository root with the command above; tests import game modules as top-level modules.
- The game loop keeps serial I/O off the rendering path.
- The repository intentionally keeps the game as flat top-level modules because `game/main.py` and the tests depend on that execution model.
- The UI prototype is retained for historical context but is not part of the supported game launch path.

## Known limitations

- Live hardware requires two BBC micro:bits and a compatible USB serial receiver.
- The game is currently designed around a desktop/fullscreen Pygame session.
- The UI prototype and firmware flashing scripts are exploratory tooling rather than a packaged application.
