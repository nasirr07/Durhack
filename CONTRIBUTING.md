# Development guide

## Supported workflow

Create a virtual environment, install `requirements.txt`, and run the test and compile checks from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s game -p "test*.py"
python -m compileall -q game
```

Run the game from `game/`:

```powershell
Set-Location game
python main.py
```

## Source layout

The supported desktop application is under `game/`. Keep its flat-import convention intact. Firmware and hardware utilities belong under `microbit-code/`; the `ui code/` directory is a separate historical prototype and should not be treated as part of the current launch path.

## Change expectations

- Keep gameplay changes focused and preserve the sensor JSON keys `temp`, `light`, and `dir`.
- Add or update focused tests for gameplay behavior.
- Treat the current unittest suite as a migration target: it contains older `Boss` API expectations, so confirm the relevant tests match the current implementation before making them a required CI gate.
- Keep serial reads off the Pygame frame loop.
- Do not commit `.env`, virtual environments, generated caches, or credentials.
- Document changes that affect setup, controls, hardware, or the supported launch path.
