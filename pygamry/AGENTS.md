# Agents Guide to pygamry

This document provides a deep dive into the `pygamry` repository, designed to help an agent (artificial or otherwise) understand, maintain, and refactor the codebase. It breaks down the system from high-level orchestration to low-level hardware interaction.

## High-Level Architecture

The repository is split into two main components:
1.  `pygamry/`: The core library containing logic for interacting with Gamry potentiostats, data processing, and plotting.
2.  `measure_scripts/`: executable scripts that use `pygamry` to run specific experiments (e.g., CV, EIS, OCV).

### Experiment Execution Flow

A typical experiment follows this sequence:
1.  **Entry Point**: A script in `measure_scripts/` (e.g., `measure_cv.py`) is executed.
2.  **Configuration**: Arguments are parsed using `argparse`, often extended by `arg_config.py`.
3.  **Initialization**:
    *   A `Dtaq` class (e.g., `DtaqCV` from `pygamry/dtaq/cv.py`) is instantiated.
    *   The `Dtaq` class initializes the Gamry Potentiostat (COM object) via `pygamry/dtaq/config.py`.
4.  **Run**: The script calls `.run()` on the `Dtaq` instance.
5.  **Event Loop**: The `.run()` method starts the hardware and enters a `PumpEvents` loop, waiting for data from the potentiostat.
6.  **Completion**: When the experiment finishes, data is written to files (`.DTA`) and connections are closed.

## Detailed Experiment Loop Analysis

The core of the experiment execution lies in `pygamry/dtaq/eventsink.py`, specifically the `GamryDtaqEventSink` class. This class wraps the COM events from the Gamry software.

### The Loop: `PumpEvents`
The `run_main()` method in `eventsink.py` sets up the experiment and then calls:
```python
self.PumpEvents(timeout)
```
This is a critical loop that:
*   Uses `ctypes` to wait for Windows events.
*   Keeps the script alive while the hardware is running.
*   Detects `KeyboardInterrupt` (CTRL+C) to safely stop experiments.

### The Events
While `PumpEvents` runs, the Gamry hardware fires events that are caught by the `GamryDtaqEventSink`:

1.  **`_IGamryDtaqEvents_OnDataAvailable`**: Fired when new data points are ready in the hardware buffer.
    *   **Action**: Calls `self.cook()`.
    *   **Action**: Calls `self.write_to_files(counts, False)`.
2.  **`_IGamryDtaqEvents_OnDataDone`**: Fired when the experiment completes naturally.
    *   **Action**: Performs a final `cook()`.
    *   **Action**: Sets `measurement_complete = True`.
    *   **Action**: Closes the connection to the potentiostat.

### The Actions (Low Level)

#### 1. `cook()`
Converting raw binary data from the hardware into Python-usable numbers.
*   Calls `self.dtaq.Cook(num_points)`.
*   Appends the cooked data to `self.acquired_points`.
*   Update `self.total_points`.

#### 2. `write_to_files()`
Persisting data to disk.
*   **Format**: Typically tab-separated values (TSV) with a header.
*   **File Types**:
    *   **Result File** (`.DTA`): The main data record.
    *   **Kst File** (`Kst_*.DTA`): A temporary file often used for live plotting interaction with external tools like Kst.
*   **Buffer Management**: Writes data in chunks (intervals) or continuously, tracking `_last_write_index` to avoid duplicating writes.

## Refactoring Roadmap for Agents

If you are refactoring this codebase, consider the following:

1.  **Decouple Data Acquisition from Event Sinking**:
    Currently, `GamryDtaqEventSink` handles *everything*: running the signal, catching events, data storage, and plotting. It is a "God Class".
    *   *Plan*: Split into `ExperimentRunner`, `DataStorage`, and `Plotter` classes.

2.  **Standardize Configuration**:
    Configuration is currently a mix of `argparse` objects passed around and loose dictionary lookups.
    *   *Plan*: Introduce a Typed `Config` object (using `pydantic` or `dataclasses`) that validates parameters before an experiment starts.

3.  **Abstract the COM Layer**:
    Direct `comtypes.client` calls are scattered.
    *   *Plan*: Create a specific `GamryHardwareInterface` that hides all `comtypes` calls. This would allow for easier mocking and testing without physical hardware (critical for CI/CD).

4.  **Unified Experiment Runner**:
    Instead of separate `measure_*.py` scripts duplicating setup logic, create a CLI runner that takes a config file (YAML/JSON) and dynamically loads the correct `Dtaq` class.

## Key Files to Watch

*   `pygamry/dtaq/eventsink.py`: The heart of the beast.
*   `pygamry/dtaq/config.py`: Magic strings and COM configuration.
*   `measure_scripts/run_functions.py`: Contains "business logic" for complex multi-step protocols like Hybrid or Staircase steps.
