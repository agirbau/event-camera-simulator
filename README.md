# Event-Camera Simulator

This tool enables simulating an event camera inside a blender scene.

It is based on the works of:

- [IEBCS](https://github.com/neuromorphicsystems/IEBCS)
- [ESIM](https://github.com/uzh-rpg/rpg_esim)

## Installation

Tested and developed on macos using Python 3.11.

- Install prerequisites
  - [UV](https://docs.astral.sh/uv/getting-started/installation/)
- Clone Repository
- Run UV sync to ensure the python verions and dependencies
```bash
uv sync
```

## Run Simulation

1. Adjust the configuration in the config file
2. Run the render command (config.yaml is the default configuration file)
```bash
uv run render --config config.yaml
```
3. Inspect the outputs in the `/temp` folder