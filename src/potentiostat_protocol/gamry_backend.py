from __future__ import annotations

import importlib
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional

from src.potentiostat_protocol.executor import DEFAULT_PARAMETERS
from src.potentiostat_protocol.schema import RuntimeConfig


class GamryBackend:
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root).resolve()
        self._loaded = False
        self._arg_defaults: Dict[str, Any] = {}
        self._pstat = None

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return

        pygamry_root = self.repo_root / "pygamry"
        measure_scripts_root = pygamry_root / "measure_scripts"
        for candidate in (pygamry_root, measure_scripts_root):
            candidate_path = str(candidate)
            if candidate_path not in sys.path:
                sys.path.insert(0, candidate_path)

        try:
            self._arg_config = importlib.import_module("arg_config")
            self._rf = importlib.import_module("run_functions")
            dtaq = importlib.import_module("pygamry.dtaq")
            reduction = importlib.import_module("pygamry.reduction")
        except Exception as exc:
            raise RuntimeError(
                "Unable to import pygamry runtime dependencies. "
                "Ensure the local pygamry project dependencies are installed."
            ) from exc

        self._get_pstat = getattr(dtaq, "get_pstat")
        self._DtaqOcv = getattr(dtaq, "DtaqOcv")
        self._DtaqReadZ = getattr(dtaq, "DtaqReadZ")
        self._DtaqPwrPol = getattr(dtaq, "DtaqPwrPol")
        self._DtaqPstatic = getattr(dtaq, "DtaqPstatic")
        self._DtaqChrono = getattr(dtaq, "DtaqChrono")
        self._HybridSequencer = getattr(dtaq, "HybridSequencer")
        self._GamryCOM = getattr(dtaq, "GamryCOM")
        self._DtaqReduction = getattr(reduction, "DtaqReduction")

        self._arg_defaults = self._extract_defaults()
        self._loaded = True

    def _extract_defaults(self) -> Dict[str, Any]:
        defaults: Dict[str, Any] = {}
        arg_dict_names = [
            "common_args",
            "ocp_args",
            "eis_args",
            "pstatic_args",
            "pwrpol_args",
            "chrono_decimate_args",
            "chrono_step_args",
            "hybrid_args",
            "staircase_args",
            "equil_args",
            "pstatic_equil_args",
            "gstatic_equil_args",
            "vsweep_args",
        ]
        for arg_dict_name in arg_dict_names:
            arg_dict = getattr(self._arg_config, arg_dict_name, {})
            for arg_name, arg_meta in arg_dict.items():
                key = str(arg_name).strip("-").replace("-", "_").lower()
                if "default" in arg_meta:
                    defaults[key] = arg_meta["default"]
                elif arg_meta.get("action") == "store_true":
                    defaults[key] = False
                elif arg_meta.get("action") == "store_false":
                    defaults[key] = True
        return defaults

    @property
    def pstat(self) -> Any:
        self._ensure_loaded()
        if self._pstat is None:
            self._pstat = self._get_pstat()
        return self._pstat

    def _build_args(
        self, runtime: RuntimeConfig, params: Dict[str, Any], file_suffix: Optional[str] = None
    ) -> SimpleNamespace:
        self._ensure_loaded()
        merged: Dict[str, Any] = {}
        merged.update(self._arg_defaults)
        merged.update(DEFAULT_PARAMETERS)
        merged.update(params)
        merged["data_path"] = runtime.data_path
        merged["file_suffix"] = file_suffix or runtime.file_suffix
        merged["exp_notes"] = runtime.exp_notes
        merged["kst_path"] = runtime.kst_path
        merged["num_loops"] = runtime.num_loops
        return SimpleNamespace(**merged)

    def _new_hybrid_sequencer(self, args: SimpleNamespace, update_step_size: bool) -> Any:
        try:
            return self._HybridSequencer(
                chrono_mode="galv",
                eis_mode=args.hybrid_eis_mode,
                update_step_size=update_step_size,
                exp_notes=args.exp_notes,
            )
        except TypeError:
            sequencer = self._HybridSequencer(
                mode="galv",
                update_step_size=update_step_size,
                exp_notes=args.exp_notes,
            )
            if hasattr(sequencer, "eis_mode"):
                sequencer.eis_mode = args.hybrid_eis_mode
            return sequencer

    def run_ocv(
        self, runtime: RuntimeConfig, params: Dict[str, Any], suffix: str, show_plot: bool
    ) -> float:
        args = self._build_args(runtime, params, file_suffix=suffix)
        ocv = self._DtaqOcv(write_mode="interval", write_interval=1, exp_notes=args.exp_notes)
        self._rf.run_ocv(ocv, self.pstat, args, suffix, show_plot=show_plot)
        try:
            return float(ocv.get_ocv(10))
        except Exception:
            return float(self._rf.test_ocv(self.pstat, num_points=3))

    def test_ocv(
        self, runtime: RuntimeConfig, params: Dict[str, Any], num_points: int = 3
    ) -> float:
        _ = self._build_args(runtime, params)
        return float(self._rf.test_ocv(self.pstat, num_points=num_points))

    def run_eis(
        self,
        runtime: RuntimeConfig,
        params: Dict[str, Any],
        suffix: str,
        v_oc: Optional[float],
        show_plot: bool,
        start_with_cell_off: Optional[bool] = None,
    ) -> None:
        args = self._build_args(runtime, params, file_suffix=suffix)
        eis = self._DtaqReadZ(
            mode=args.eis_mode,
            readzspeed="ReadZSpeedNorm",
            write_mode="interval",
            write_interval=1,
            exp_notes=args.exp_notes,
        )
        if start_with_cell_off is not None and hasattr(eis, "start_with_cell_off"):
            eis.start_with_cell_off = start_with_cell_off
        self._rf.run_eis(eis, self.pstat, args, suffix, V_oc=v_oc, show_plot=show_plot)

    def run_pwrpol(
        self, runtime: RuntimeConfig, params: Dict[str, Any], suffix: str, show_plot: bool
    ) -> str:
        args = self._build_args(runtime, params, file_suffix=suffix)
        pwrpol = self._DtaqPwrPol(
            write_mode="interval", write_interval=1, exp_notes=args.exp_notes
        )
        self._rf.run_pwrpol(pwrpol, self.pstat, args, suffix, show_plot=show_plot)
        return os.path.join(args.data_path, f"PWRPOLARIZATION_{suffix}.DTA")

    def run_pstatic(
        self,
        runtime: RuntimeConfig,
        params: Dict[str, Any],
        suffix: str,
        v_oc: Optional[float],
        pwrpol_data: Optional[Any] = None,
        show_plot: bool = False,
    ) -> None:
        args = self._build_args(runtime, params, file_suffix=suffix)
        pstatic = self._DtaqPstatic(
            write_mode="interval",
            write_interval=1,
            exp_notes=args.exp_notes,
            leave_cell_on=True,
        )
        self._rf.run_pstatic(
            pstatic,
            self.pstat,
            args,
            suffix,
            V_oc=v_oc,
            pwrpol_dtaq=pwrpol_data,
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
        args = self._build_args(runtime, params, file_suffix=suffix)
        chrono = self._DtaqChrono(
            mode,
            write_mode="once",
            write_precision=6,
            exp_notes=args.exp_notes,
        )
        if repeats > 1:
            chrono.leave_cell_on = True
            chrono.start_with_cell_off = False
        self._rf.run_chrono(
            chrono,
            self.pstat,
            args,
            suffix,
            show_plot=runtime.show_plot,
            repeats=repeats,
        )

    def run_repeating_gstep_chronop(
        self, runtime: RuntimeConfig, params: Dict[str, Any]
    ) -> None:
        args = self._build_args(runtime, params, file_suffix=runtime.file_suffix)
        chrono = self._DtaqChrono(
            "galv",
            write_mode="once",
            write_precision=6,
            exp_notes=args.exp_notes,
            leave_cell_on=True,
            start_with_cell_off=False,
        )

        if args.chrono_v_rms is not None and not args.chrono_disable_find_i:
            v_oc = self._rf.test_ocv(self.pstat)
            s_rms = self._rf.find_current(self.pstat, v_oc + args.chrono_v_rms, 2.0)
            s_half_step = s_rms * (2**0.5)
            args.chrono_geo_s_final = args.chrono_s_init
            args.chrono_geo_s_min = min(args.chrono_s_init, args.chrono_s_init + 2 * s_half_step)
            args.chrono_geo_s_max = max(args.chrono_s_init, args.chrono_s_init + 2 * s_half_step)

        decimate = not args.disable_decimation
        if decimate:
            chrono.configure_decimation(
                args.decimate_during,
                args.decimation_prestep_points,
                args.decimation_interval,
                args.decimation_factor,
                args.decimation_max_t_sample,
            )

        chrono.configure_geostep_signal(
            args.chrono_s_init,
            args.chrono_geo_s_final,
            args.chrono_geo_s_min,
            args.chrono_geo_s_max,
            args.chrono_t_init,
            args.chrono_t_sample,
            args.chrono_geo_t_short,
            args.chrono_t_step,
            args.chrono_geo_num_scales,
            args.chrono_geo_steps_per_scale,
        )
        result_file = os.path.join(args.data_path, f"CHRONOP_{args.file_suffix}.DTA")
        kst_file = (
            os.path.join(args.kst_path, "Kst_IVT.DTA") if args.kst_path is not None else None
        )
        chrono.run(
            self.pstat,
            result_file=result_file,
            kst_file=kst_file,
            decimate=decimate,
            show_plot=False,
            repeats=args.repeats,
        )

    def run_vsweep(
        self, runtime: RuntimeConfig, params: Dict[str, Any], suffix: str, v_oc: float
    ) -> Any:
        args = self._build_args(runtime, params, file_suffix=suffix)
        chrono = self._DtaqChrono(
            mode="pot", write_mode="once", write_precision=6, exp_notes=args.exp_notes
        )
        return self._rf.run_v_sweep(chrono, self.pstat, args, suffix, V_oc=v_oc)

    def load_vsweep_file(self, path: str) -> Any:
        try:
            import pandas as pd

            return pd.read_csv(path, sep="\t")
        except Exception:
            return path

    def run_hybrid(
        self,
        runtime: RuntimeConfig,
        params: Dict[str, Any],
        suffix: str,
        show_plot: bool,
        start_with_cell_off: bool = True,
        leave_cell_on: bool = True,
    ) -> Dict[str, float]:
        args = self._build_args(runtime, params, file_suffix=suffix)
        seq = self._new_hybrid_sequencer(args, update_step_size=True)
        self._rf.run_hybrid(
            seq,
            self.pstat,
            args,
            suffix,
            show_plot=show_plot,
            start_with_cell_off=start_with_cell_off,
            leave_cell_on=leave_cell_on,
        )
        return {
            "meas_v_min": float(getattr(seq, "meas_v_min", 0.0)),
            "meas_v_max": float(getattr(seq, "meas_v_max", 0.0)),
            "meas_v_end": float(getattr(seq, "meas_v_end", 0.0)),
        }

    def run_hybrid_staircase(
        self,
        runtime: RuntimeConfig,
        params: Dict[str, Any],
        suffix: str,
        jv_data: Optional[Any] = None,
    ) -> None:
        args = self._build_args(runtime, params, file_suffix=suffix)
        update_step_size = not bool(args.staircase_constant_step_size)
        seq = self._new_hybrid_sequencer(args, update_step_size=update_step_size)
        self._rf.run_hybrid_staircase(seq, self.pstat, args, suffix, jv_data=jv_data)

    def run_conditioning_hybrid(
        self, runtime: RuntimeConfig, params: Dict[str, Any], suffix: str
    ) -> None:
        args = self._build_args(runtime, params, file_suffix=suffix)
        chrono = self._DtaqChrono(mode="galv")
        chrono.configure_mstep_signal(
            0,
            args.hybrid_i_init,
            1,
            args.condition_time,
            args.condition_t_sample,
            n_steps=1,
        )
        chrono.leave_cell_on = True
        chrono.configure_decimation("write", 20, 10, 2, 1)
        chrono_file = os.path.join(args.data_path, f"Conditioning_{suffix}.DTA")
        kst_file = (
            os.path.join(args.kst_path, "Kst_IVT.DTA") if args.kst_path is not None else None
        )
        chrono.run(self.pstat, result_file=chrono_file, kst_file=kst_file, decimate=True)

    def run_pstatic_finish(
        self, runtime: RuntimeConfig, params: Dict[str, Any], i_sign: int
    ) -> None:
        args = self._build_args(runtime, params)
        pstatic = self._DtaqPstatic()
        if i_sign < 0:
            i_min = -abs(args.finish_i_max)
            i_max = -abs(args.finish_i_thresh)
        else:
            i_min = abs(args.finish_i_thresh)
            i_max = abs(args.finish_i_max)
        result_file = os.path.join(args.data_path, f"PSTATIC-FINISH_{args.file_suffix}.DTA")
        kst_file = (
            os.path.join(args.kst_path, "Kst_IVT.DTA") if args.kst_path is not None else None
        )
        pstatic.run(
            self.pstat,
            args.finish_v,
            args.finish_duration,
            args.finish_t_sample,
            i_min=i_min,
            i_max=i_max,
            result_file=result_file,
            kst_file=kst_file,
        )

    def equilibrate(self, runtime: RuntimeConfig, params: Dict[str, Any], suffix: str) -> None:
        args = self._build_args(runtime, params, file_suffix=suffix)
        self._rf.equilibrate(self.pstat, args, suffix)

    def run_reduction(self, runtime: RuntimeConfig, params: Dict[str, Any], suffix: str) -> None:
        args = self._build_args(runtime, params, file_suffix=suffix)
        dtaq = self._DtaqReduction(
            args.reduction_config_file,
            write_mode="interval",
            write_interval=1,
            exp_notes=args.exp_notes,
        )
        result_file = os.path.join(args.data_path, f"OCP_{args.file_suffix}.DTA")
        kst_file = (
            os.path.join(args.kst_path, "Kst_OCP.DTA") if args.kst_path is not None else None
        )
        dtaq.run(
            self.pstat,
            args.ocp_duration,
            args.ocp_sample_period,
            args.data_path,
            result_file=result_file,
            kst_file=kst_file,
            show_plot=False,
        )

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def shutdown_pstat(self) -> None:
        if self._pstat is None:
            return
        try:
            if self._pstat.TestIsOpen():
                self._pstat.SetCell(self._GamryCOM.CellOff)
                self._pstat.Close()
        except Exception:
            pass
