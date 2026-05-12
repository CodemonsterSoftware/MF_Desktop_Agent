# Model Foundry Desktop Agent

This is the standalone desktop agent for Model Foundry. It runs in the system tray and monitors slicer output directories (Bambu Studio, OrcaSlicer, etc.) for `.gcode` and `.3mf` files, parsing print metadata and forwarding it to the Model Foundry server.

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the agent:
   ```bash
   python main.py
   ```

## Building Executable

To build a standalone executable for Windows:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=assets/icon.png main.py -n modelfoundry_agent
```

The compiled `.exe` will be located in the `dist/` directory.
