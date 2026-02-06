from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from src.potentiostat_protocol.schema import PotentiostatExperiment, RuntimeConfig


DEFAULT_PARAMETERS: Dict[str, Any] = {
    "ocp_duration": 600.0,
    "ocp_sample_period": 1.0,
    "eis_mode": "pot",
    "eis_z_guess": 5.0,
    "eis_speed": "Norm",
    "eis_max_freq": 1e6,
    "eis_min_freq": 0.1,
    "eis_ppd": 10,
    "eis_sac": 0.01,
    "eis_sdc": 0.0,
    "eis_vdc_vs_vref": False,
    "eis_condition_time": 0.0,
    "pstatic_vdc": 0.8,
    "pstatic_duration": 600.0,
    "pstatic_sample_period": 1.0,
    "pstatic_i_min": None,
    "pstatic_i_max": None,
    "pstatic_vdc_vs_vref": False,
    "pwrpol_i_final": 1.0,
    "pwrpol_scan_rate": 0.001,
    "pwrpol_sample_period": 5.0,
    "pwrpol_v_min": 0.4,
    "pwrpol_v_max": 1.5,
    "pwrpol_direction": "both",
    "pwrpol_rest_time": 60.0,
    "disable_decimation": False,
    "decimate_during": "write",
    "decimation_prestep_points": 20,
    "decimation_interval": 30,
    "decimation_factor": 2.0,
    "decimation_max_t_sample": 0.05,
    "decimate_filter": False,
    "chrono_mode": "galv",
    "chrono_v_rms": 0.01,
    "chrono_disable_find_i": False,
    "chrono_step_type": "dstep",
    "chrono_s_init": 0.0,
    "chrono_t_init": 0.1,
    "chrono_t_sample": 1e-4,
    "chrono_s_step1": -1e-4,
    "chrono_s_step2": 0.0,
    "chrono_t_step1": 1.0,
    "chrono_t_step2": 1.0,
    "chrono_s_step": 1e-4,
    "chrono_t_step": 1.0,
    "chrono_n_steps": 1,
    "chrono_s_rms": 0.01,
    "chrono_geo_s_final": 0.0,
    "chrono_geo_s_min": 0.0,
    "chrono_geo_s_max": 0.0,
    "chrono_geo_t_short": 1e-3,
    "chrono_geo_num_scales": 3,
    "chrono_geo_steps_per_scale": 2,
    "hybrid_step_type": "triple",
    "hybrid_i_init": 0.0,
    "hybrid_i_rms": 0.01,
    "hybrid_v_rms": 0.01,
    "hybrid_disable_find_i": False,
    "hybrid_t_init": 0.1,
    "hybrid_t_step": 1.0,
    "hybrid_geo_t_short": 1e-3,
    "hybrid_geo_num_scales": 3,
    "hybrid_geo_steps_per_scale": 2,
    "hybrid_geo_end_at_init": False,
    "hybrid_geo_end_time": 0.0,
    "hybrid_chrono_first": False,
    "hybrid_t_sample": 1e-4,
    "hybrid_eis_max_freq": 1e6,
    "hybrid_eis_min_freq": 1e3,
    "hybrid_eis_ppd": 10,
    "hybrid_eis_mode": "galv",
    "hybrid_rest_time": 0.0,
    "hybrid_z_guess": 1.0,
    "staircase_v_min": 0.4,
    "staircase_v_max": 1.5,
    "staircase_num_steps": 20,
    "staircase_constant_step_size": False,
    "staircase_equil_time": 60.0,
    "staircase_ocv_equil": False,
    "staircase_run_post_eis": False,
    "staircase_run_pre_eis": False,
    "staircase_direction": "both",
    "staircase_full_eis_max_freq": 1e6,
    "staircase_full_eis_min_freq": 1e-1,
    "staircase_full_eis_ppd": 10,
    "vsweep_v_rms": 0.01,
    "vsweep_t_init": 1.0,
    "vsweep_t_sample": 1e-2,
    "vsweep_t_step": 5.0,
    "vsweep_num_steps": 20,
    "vsweep_direction": "both",
    "vsweep_v_min": 0.4,
    "vsweep_v_max": 1.5,
    "vsweep_rest_time": 60.0,
    "vsweep_ocv_equil": False,
    "vsweep_i_max": 1.0,
    "vsweep_file": "none",
    "disable_vsweep": False,
    "min_i_step": -1.0,
    "equil_mode": "pot",
    "equil_duration": 600.0,
    "equil_sample_period": 0.01,
    "equil_window_seconds": 15.0,
    "equil_slope_thresh": 0.25,
    "equil_min_wait_time": 0.0,
    "equil_require_consecutive": 10,
    "pequil_vdc": -0.1,
    "pequil_i_min": None,
    "pequil_i_max": None,
    "pequil_vdc_vs_vref": False,
    "gequil_idc": 0.0,
    "gequil_vdc": None,
    "gequil_vdc_vs_vref": False,
    "gequil_v_min": None,
    "gequil_v_max": None,
    "repeats": 1,
    "max_repeats": 1,
    "condition_time": 0.0,
    "condition_t_sample": 1e-3,
    "stop_v_min": -1.0,
    "stop_v_max": 1.0,
    "duration": 3600.0,
    "voltage_finish": False,
    "finish_v": 0.0,
    "finish_i_thresh": 0.005,
    "finish_i_max": 1.0,
    "finish_t_sample": 1.0,
    "finish_duration": 3600.0,
    "finish_rest_time": 2.0,
    "charge_voltage_finish": False,
    "charge_finish_v": 0.0,
    "charge_finish_i_thresh": 0.001,
    "charge_finish_t_sample": 1.0,
    "charge_finish_duration": 3600.0,
    "charge_finish_rest_time": 60.0,
}


def _sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


class DryRunBackend:
    def __init__(self, hybrid_outcomes: Optional[List[Dict[str, float]]] = None):
        self.records: List[Dict[str, Any]] = []
        self._hybrid_outcomes = list(hybrid_outcomes or [])

    def _record(self, operation: str, **fields: Any) -> None:
        payload = {"operation": operation}
        payload.update(fields)
        self.records.append(payload)

    def run_ocv(
        self, runtime: RuntimeConfig, params: Dict[str, Any], suffix: str, show_plot: bool
    ) -> float:
        self._record("run_ocv", suffix=suffix, show_plot=show_plot)
        return float(params.get("sim_ocv", 0.0))

    def test_ocv(
        self, runtime: RuntimeConfig, params: Dict[str, Any], num_points: int = 3
    ) -> float:
        self._record("test_ocv", num_points=num_points)
        return float(params.get("sim_ocv", 0.0))

    def run_eis(
        self,
        runtime: RuntimeConfig,
        params: Dict[str, Any],
        suffix: str,
        v_oc: Optional[float],
        show_plot: bool,
        start_with_cell_off: Optional[bool] = None,
    ) -> None:
        self._record(
            "run_eis",
            suffix=suffix,
            v_oc=v_oc,
            show_plot=show_plot,
            start_with_cell_off=start_with_cell_off,
        )

    def run_pwrpol(
        self, runtime: RuntimeConfig, params: Dict[str, Any], suffix: str, show_plot: bool
    ) -> str:
        self._record("run_pwrpol", suffix=suffix, show_plot=show_plot)
        return f"{runtime.data_path}/PWRPOLARIZATION_{suffix}.DTA"

    def run_pstatic(
        self,
        runtime: RuntimeConfig,
        params: Dict[str, Any],
        suffix: str,
        v_oc: Optional[float],
        pwrpol_data: Optional[Any] = None,
        show_plot: bool = False,
    ) -> None:
        self._record(
            "run_pstatic",
            suffix=suffix,
            v_oc=v_oc,
            pwrpol_data=bool(pwrpol_data),
            show_plot=show_plot,
        )

    def run_chrono(
        self,
        runtime: RuntimeConfig,
        params: Dict[str, Any],
        suffix: str,
        repeats: int = 1,
        mode: str = "galv",
    ) -> None:
        self._record("run_chrono", suffix=suffix, repeats=repeats, mode=mode)

    def run_repeating_gstep_chronop(
        self, runtime: RuntimeConfig, params: Dict[str, Any]
    ) -> None:
        self._record("run_repeating_gstep_chronop", repeats=params.get("repeats", 1))

    def run_vsweep(
        self,
        runtime: RuntimeConfig,
        params: Dict[str, Any],
        suffix: str,
        v_oc: float,
    ) -> Dict[str, Any]:
        self._record("run_vsweep", suffix=suffix, v_oc=v_oc)
        return {"source": "vsweep", "suffix": suffix}

    def load_vsweep_file(self, path: str) -> Dict[str, Any]:
        self._record("load_vsweep_file", path=path)
        return {"source": "file", "path": path}

    def run_hybrid(
        self,
        runtime: RuntimeConfig,
        params: Dict[str, Any],
        suffix: str,
        show_plot: bool,
        start_with_cell_off: bool = True,
        leave_cell_on: bool = True,
    ) -> Dict[str, float]:
        self._record(
            "run_hybrid",
            suffix=suffix,
            show_plot=show_plot,
            start_with_cell_off=start_with_cell_off,
            leave_cell_on=leave_cell_on,
        )
        if self._hybrid_outcomes:
            return self._hybrid_outcomes.pop(0)
        return {"meas_v_min": 0.0, "meas_v_max": 0.0, "meas_v_end": 0.0}

    def run_hybrid_staircase(
        self,
        runtime: RuntimeConfig,
        params: Dict[str, Any],
        suffix: str,
        jv_data: Optional[Any] = None,
    ) -> None:
        self._record("run_hybrid_staircase", suffix=suffix, has_jv_data=jv_data is not None)

    def run_conditioning_hybrid(
        self, runtime: RuntimeConfig, params: Dict[str, Any], suffix: str
    ) -> None:
        self._record("run_conditioning_hybrid", suffix=suffix)

    def run_pstatic_finish(
        self, runtime: RuntimeConfig, params: Dict[str, Any], i_sign: int
    ) -> None:
        self._record("run_pstatic_finish", i_sign=i_sign)

    def equilibrate(self, runtime: RuntimeConfig, params: Dict[str, Any], suffix: str) -> None:
        self._record("equilibrate", suffix=suffix)

    def run_reduction(self, runtime: RuntimeConfig, params: Dict[str, Any], suffix: str) -> None:
        self._record("run_reduction", suffix=suffix)

    def sleep(self, seconds: float) -> None:
        self._record("sleep", seconds=seconds)

    def shutdown_pstat(self) -> None:
        self._record("shutdown_pstat")


class PotentiostatExecutor:
    def __init__(self, backend: Any):
        self.backend = backend

    def execute(self, experiment: PotentiostatExperiment) -> None:
        params = self._merged_parameters(experiment)
        workflow_name = experiment.workflow
        handler_name = f"_execute_{workflow_name}"
        if not hasattr(self, handler_name):
            raise ValueError(f"Unsupported workflow '{workflow_name}'")
        handler = getattr(self, handler_name)
        handler(experiment.runtime, params)

    def _merged_parameters(self, experiment: PotentiostatExperiment) -> Dict[str, Any]:
        merged = dict(DEFAULT_PARAMETERS)
        merged.update(experiment.parameters)
        return merged

    def _loop_suffix(self, base: str, index: int, total: int, style: str) -> str:
        if total <= 1:
            return base
        if style == "cycle":
            return f"{base}_Cycle{index}"
        return f"{base}_#{index}"

    def _execute_measure_ocp(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            self.backend.run_ocv(runtime, params, suffix, show_plot=False)
            self.backend.sleep(1.0)

    def _execute_measure_eis(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            v_oc = self.backend.test_ocv(runtime, params, num_points=9)
            self.backend.run_eis(runtime, params, suffix, v_oc=v_oc, show_plot=False)

    def _execute_measure_ocp_eis(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            v_oc = self.backend.run_ocv(runtime, params, suffix, show_plot=False)
            self.backend.sleep(1.0)
            self.backend.run_eis(runtime, params, suffix, v_oc=v_oc, show_plot=False)
            self.backend.sleep(1.0)

    def _execute_measure_pwrpol(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            self.backend.run_pwrpol(runtime, params, suffix, show_plot=False)
            self.backend.sleep(1.0)

    def _execute_measure_basic_performance(
        self, runtime: RuntimeConfig, params: Dict[str, Any]
    ) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            v_oc = self.backend.run_ocv(runtime, params, suffix, show_plot=False)
            self.backend.sleep(1.0)
            self.backend.run_eis(runtime, params, suffix, v_oc=v_oc, show_plot=False)
            self.backend.sleep(1.0)
            self.backend.run_pwrpol(runtime, params, suffix, show_plot=False)
            self.backend.sleep(1.0)

    def _execute_measure_full_performance(
        self, runtime: RuntimeConfig, params: Dict[str, Any]
    ) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            v_oc = self.backend.run_ocv(runtime, params, suffix, show_plot=False)
            self.backend.sleep(1.0)
            self.backend.run_eis(runtime, params, suffix, v_oc=v_oc, show_plot=False)
            self.backend.sleep(1.0)
            pwrpol_result = self.backend.run_pwrpol(runtime, params, suffix, show_plot=False)
            self.backend.sleep(1.0)
            self.backend.run_hybrid_staircase(
                runtime, params, suffix, jv_data=pwrpol_result
            )
            self.backend.sleep(1.0)

    def _execute_measure_hybrid(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            self.backend.run_hybrid(
                runtime,
                params,
                suffix,
                show_plot=runtime.show_plot,
                start_with_cell_off=True,
                leave_cell_on=True,
            )

    def _execute_measure_hybrid_staircase(
        self, runtime: RuntimeConfig, params: Dict[str, Any]
    ) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            self.backend.run_hybrid_staircase(runtime, params, suffix, jv_data=None)

    def _execute_measure_vsweep(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            v_oc = self.backend.run_ocv(runtime, params, suffix, show_plot=False)
            self.backend.sleep(1.0)
            self.backend.run_vsweep(runtime, params, suffix, v_oc=v_oc)

    def _execute_measure_pol_map(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            v_oc = self.backend.run_ocv(runtime, params, suffix, show_plot=False)
            self.backend.sleep(1.0)

            vsweep_file = str(params.get("vsweep_file", "none"))
            if vsweep_file.lower() != "none":
                iv_data = self.backend.load_vsweep_file(vsweep_file)
            elif not bool(params.get("disable_vsweep", False)):
                iv_data = self.backend.run_vsweep(runtime, params, suffix, v_oc=v_oc)
            else:
                iv_data = None

            self.backend.run_hybrid_staircase(runtime, params, suffix, jv_data=iv_data)
            self.backend.sleep(1.0)

    def _execute_measure_pstatic(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            v_oc = self.backend.test_ocv(runtime, params)
            self.backend.run_pstatic(
                runtime, params, suffix, v_oc=v_oc, pwrpol_data=None, show_plot=False
            )

            bias_params = dict(params)
            bias_params["eis_sdc"] = params["pstatic_vdc"]
            bias_params["eis_vdc_vs_vref"] = params["pstatic_vdc_vs_vref"]
            bias_suffix = f"VDC={params['pstatic_vdc']}_{suffix}"
            self.backend.run_eis(
                runtime,
                bias_params,
                bias_suffix,
                v_oc=v_oc,
                show_plot=False,
                start_with_cell_off=False,
            )
            self.backend.sleep(1.0)

    def _execute_measure_pstatic_stability(
        self, runtime: RuntimeConfig, params: Dict[str, Any]
    ) -> None:
        for index in range(runtime.num_loops):
            suffix = self._loop_suffix(runtime.file_suffix, index, runtime.num_loops, "hash")
            v_oc = self.backend.test_ocv(runtime, params)
            self.backend.run_pstatic(
                runtime, params, suffix, v_oc=v_oc, pwrpol_data=None, show_plot=False
            )

            bias_params = dict(params)
            bias_params["eis_sdc"] = params["pstatic_vdc"]
            bias_params["eis_vdc_vs_vref"] = params["pstatic_vdc_vs_vref"]
            bias_suffix = f"VDC={params['pstatic_vdc']}_{suffix}"
            self.backend.run_eis(
                runtime,
                bias_params,
                bias_suffix,
                v_oc=v_oc,
                show_plot=False,
                start_with_cell_off=False,
            )

            v_oc = self.backend.run_ocv(runtime, params, suffix, show_plot=False)
            self.backend.sleep(1.0)
            self.backend.run_eis(
                runtime,
                params,
                suffix,
                v_oc=v_oc,
                show_plot=False,
                start_with_cell_off=True,
            )
            self.backend.sleep(1.0)
            self.backend.run_pwrpol(runtime, params, suffix, show_plot=False)
            self.backend.sleep(1.0)

    def _execute_measure_chrono(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        self.backend.run_chrono(
            runtime,
            params,
            runtime.file_suffix,
            repeats=1,
            mode=str(params.get("chrono_mode", "galv")),
        )

    def _execute_measure_repeating_dstep_chronop(
        self, runtime: RuntimeConfig, params: Dict[str, Any]
    ) -> None:
        repeats = int(params.get("repeats", 1))
        self.backend.run_chrono(
            runtime,
            params,
            runtime.file_suffix,
            repeats=repeats,
            mode="galv",
        )
        self.backend.shutdown_pstat()

    def _execute_measure_repeating_gstep_chronop(
        self, runtime: RuntimeConfig, params: Dict[str, Any]
    ) -> None:
        self.backend.run_repeating_gstep_chronop(runtime, params)
        self.backend.shutdown_pstat()

    def _execute_measure_repeating_hybrid(
        self, runtime: RuntimeConfig, params: Dict[str, Any]
    ) -> None:
        repeats = int(params.get("repeats", 1))
        start_with_cell_off = True
        if float(params.get("condition_time", 0.0)) > 0:
            self.backend.run_conditioning_hybrid(runtime, params, runtime.file_suffix)
            start_with_cell_off = False

        leave_cell_on = True
        for index in range(repeats):
            suffix = self._loop_suffix(runtime.file_suffix, index, repeats, "cycle")
            if index > 0:
                start_with_cell_off = False
            if index == repeats - 1:
                leave_cell_on = False

            self.backend.run_hybrid(
                runtime,
                params,
                suffix,
                show_plot=False,
                start_with_cell_off=start_with_cell_off,
                leave_cell_on=leave_cell_on,
            )

    def _execute_charge_hybrid(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        max_repeats = int(params.get("max_repeats", 1))
        start_with_cell_off = True
        i_sign = _sign(float(params.get("hybrid_i_init", 0.0)))
        start_time = time.monotonic()

        if float(params.get("condition_time", 0.0)) > 0:
            self.backend.run_conditioning_hybrid(runtime, params, runtime.file_suffix)
            start_with_cell_off = False

        leave_cell_on = True
        for index in range(max_repeats):
            suffix = self._loop_suffix(runtime.file_suffix, index, max_repeats, "cycle")
            if index > 0:
                start_with_cell_off = False
            if index == max_repeats - 1:
                leave_cell_on = False

            metrics = self.backend.run_hybrid(
                runtime,
                params,
                suffix,
                show_plot=False,
                start_with_cell_off=start_with_cell_off,
                leave_cell_on=leave_cell_on,
            )

            stop = False
            if metrics.get("meas_v_min", 0.0) <= float(params.get("stop_v_min", -1.0)):
                stop = True
            if metrics.get("meas_v_max", 0.0) >= float(params.get("stop_v_max", 1.0)):
                stop = True
            if bool(params.get("voltage_finish", False)) and (
                metrics.get("meas_v_end", 0.0) * i_sign
                >= float(params.get("finish_v", 0.0)) * i_sign
            ):
                stop = True

            elapsed = time.monotonic() - start_time
            if elapsed >= float(params.get("duration", 3600.0)):
                stop = True

            if stop:
                self.backend.shutdown_pstat()
                break

        if bool(params.get("voltage_finish", False)):
            self.backend.sleep(float(params.get("finish_rest_time", 2.0)))
            self.backend.run_pstatic_finish(runtime, params, i_sign=i_sign)

    def _execute_batt_hybrid_discharge_charge(
        self, runtime: RuntimeConfig, params: Dict[str, Any]
    ) -> None:
        repeats = int(params.get("repeats", 1))
        start_with_cell_off = True
        i_sign = _sign(float(params.get("hybrid_i_init", 0.0)))

        if float(params.get("condition_time", 0.0)) > 0:
            self.backend.run_conditioning_hybrid(runtime, params, runtime.file_suffix)
            start_with_cell_off = False

        leave_cell_on = True
        for index in range(repeats):
            suffix = self._loop_suffix(runtime.file_suffix, index, repeats, "cycle")
            if index > 0:
                start_with_cell_off = False
            if index == repeats - 1:
                leave_cell_on = False

            metrics = self.backend.run_hybrid(
                runtime,
                params,
                suffix,
                show_plot=False,
                start_with_cell_off=start_with_cell_off,
                leave_cell_on=leave_cell_on,
            )
            if metrics.get("meas_v_min", 0.0) <= float(params.get("stop_v_min", -1.0)):
                self.backend.shutdown_pstat()
                break
            if metrics.get("meas_v_max", 0.0) >= float(params.get("stop_v_max", 1.0)):
                self.backend.shutdown_pstat()
                break

        if bool(params.get("charge_voltage_finish", False)):
            finish_params = dict(params)
            finish_params["finish_v"] = params.get("charge_finish_v", params.get("finish_v", 0.0))
            finish_params["finish_i_thresh"] = params.get(
                "charge_finish_i_thresh", params.get("finish_i_thresh", 0.005)
            )
            finish_params["finish_t_sample"] = params.get(
                "charge_finish_t_sample", params.get("finish_t_sample", 1.0)
            )
            finish_params["finish_duration"] = params.get(
                "charge_finish_duration", params.get("finish_duration", 3600.0)
            )
            finish_params["finish_i_max"] = abs(float(params.get("hybrid_i_init", 0.0)) * 1.05)
            self.backend.sleep(float(params.get("charge_finish_rest_time", 60.0)))
            self.backend.run_pstatic_finish(runtime, finish_params, i_sign=i_sign)

    def _execute_equilibrate(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        self.backend.equilibrate(runtime, params, runtime.file_suffix)

    def _execute_run_reduction(self, runtime: RuntimeConfig, params: Dict[str, Any]) -> None:
        self.backend.run_reduction(runtime, params, runtime.file_suffix)
