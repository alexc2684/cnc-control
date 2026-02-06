from pathlib import Path

import yaml

from src.potentiostat_protocol.executor import DryRunBackend, PotentiostatExecutor
from src.potentiostat_protocol.schema import PotentiostatExperiment


def test_experiment_loads_from_yaml(tmp_path):
    payload = {
        "name": "Basic performance",
        "workflow": "measure_basic_performance",
        "runtime": {
            "data_path": ".",
            "file_suffix": "Smoke",
            "num_loops": 2,
        },
        "parameters": {
            "ocp_duration": 30.0,
            "ocp_sample_period": 1.0,
            "eis_mode": "pot",
            "eis_max_freq": 1e5,
            "eis_min_freq": 1.0,
            "eis_ppd": 5,
            "eis_sac": 0.01,
            "eis_sdc": 0.0,
            "eis_z_guess": 5.0,
            "pwrpol_direction": "both",
            "pwrpol_i_final": 0.5,
            "pwrpol_scan_rate": 0.001,
            "pwrpol_sample_period": 5.0,
            "pwrpol_v_min": 0.4,
            "pwrpol_v_max": 1.2,
            "pwrpol_rest_time": 2.0,
        },
    }
    path = tmp_path / "experiment.yaml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    experiment = PotentiostatExperiment.from_yaml(str(path))

    assert experiment.name == "Basic performance"
    assert experiment.workflow == "measure_basic_performance"
    assert experiment.runtime.num_loops == 2
    assert experiment.parameters["ocp_duration"] == 30.0


def test_measure_basic_performance_executes_expected_order():
    experiment = PotentiostatExperiment(
        name="Basic performance",
        workflow="measure_basic_performance",
        runtime={"data_path": ".", "file_suffix": "Run", "num_loops": 2},
        parameters={
            "ocp_duration": 10.0,
            "ocp_sample_period": 1.0,
            "eis_mode": "pot",
            "eis_max_freq": 1e5,
            "eis_min_freq": 10.0,
            "eis_ppd": 5,
            "eis_sac": 0.01,
            "eis_sdc": 0.0,
            "eis_z_guess": 2.0,
            "pwrpol_direction": "discharge",
            "pwrpol_i_final": 0.1,
            "pwrpol_scan_rate": 0.001,
            "pwrpol_sample_period": 3.0,
            "pwrpol_v_min": 0.4,
            "pwrpol_v_max": 1.3,
            "pwrpol_rest_time": 1.0,
        },
    )
    backend = DryRunBackend()
    executor = PotentiostatExecutor(backend)

    executor.execute(experiment)

    operation_order = [record["operation"] for record in backend.records]
    assert operation_order == [
        "run_ocv",
        "sleep",
        "run_eis",
        "sleep",
        "run_pwrpol",
        "sleep",
        "run_ocv",
        "sleep",
        "run_eis",
        "sleep",
        "run_pwrpol",
        "sleep",
    ]
    suffixes = [record["suffix"] for record in backend.records if "suffix" in record]
    assert suffixes == [
        "Run_#0",
        "Run_#0",
        "Run_#0",
        "Run_#1",
        "Run_#1",
        "Run_#1",
    ]


def test_charge_hybrid_stops_when_voltage_threshold_crosses():
    experiment = PotentiostatExperiment(
        name="Charge hybrid",
        workflow="charge_hybrid",
        runtime={"data_path": ".", "file_suffix": "Charge"},
        parameters={
            "max_repeats": 5,
            "hybrid_i_init": 0.2,
            "stop_v_min": -1.0,
            "stop_v_max": 0.6,
            "duration": 3600.0,
            "voltage_finish": False,
        },
    )
    backend = DryRunBackend(
        hybrid_outcomes=[
            {"meas_v_min": -0.2, "meas_v_max": 0.7, "meas_v_end": 0.65},
            {"meas_v_min": -0.2, "meas_v_max": 0.5, "meas_v_end": 0.4},
        ]
    )
    executor = PotentiostatExecutor(backend)

    executor.execute(experiment)

    operation_order = [record["operation"] for record in backend.records]
    assert operation_order == ["run_hybrid", "shutdown_pstat"]


def test_all_migrated_workflow_yamls_are_loadable():
    yaml_dir = Path("experiments/potentiostat")
    yaml_files = sorted(yaml_dir.glob("*.yaml"))

    assert len(yaml_files) >= 20
    for yaml_path in yaml_files:
        experiment = PotentiostatExperiment.from_yaml(str(yaml_path))
        assert experiment.name
        assert experiment.workflow
