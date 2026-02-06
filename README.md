# CNC Control Project

A standalone project for controlling a GRBL CNC mill.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Experiment Protocol Engine

This project features a robust **Protocol Engine** for defining and executing automated experiments on the CNC mill.

### Key Features
- **YAML-based Protocols**: Define experiments in simple YAML files (see `experiments/`).
- **Safe Path Planning**: Automatic "Safe Z" travel and optimization to prevent collisions.
- **Hardware Abstraction**: Clean separation between protocol logic and hardware drivers.

### Running an Experiment
1. **Configure Hardware**: Update `configs/genmitsu_3018_deck_config.yaml` with your machine bounds, camera source, and serial port.
2. **Define Experiment**: Create a YAML file in `experiments/` (e.g., `experiments/my_experiment.yaml`).
3. **Run**:
   ```bash
   python verify_experiment.py experiments/my_experiment.yaml
   ```

## Development

Run unit tests:
```bash
pytest tests/
```

## Potentiostat Protocols (pygamry Refactor)

The legacy `pygamry/measure_scripts/*.py` entrypoints are now represented as YAML workflows.

- YAML workflows: `experiments/potentiostat/*.yaml`
- Schema/execution package: `src/potentiostat_protocol/`
- Runner: `verify_potentiostat_experiment.py`

### Run a Potentiostat Workflow

Dry-run (safe, no hardware):
```bash
python verify_potentiostat_experiment.py experiments/potentiostat/measure_basic_performance.yaml --backend dry-run
```

Real hardware execution:
```bash
python verify_potentiostat_experiment.py experiments/potentiostat/measure_basic_performance.yaml --backend gamry
```
