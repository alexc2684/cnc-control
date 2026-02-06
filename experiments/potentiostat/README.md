# Potentiostat YAML Workflows

Each YAML file in this folder replaces one legacy `pygamry/measure_scripts` entrypoint:

- `measure_ocp.yaml` -> `measure_ocp.py`
- `measure_eis.yaml` -> `measure_eis.py`
- `measure_ocp_eis.yaml` -> `measure_ocp_eis.py`
- `measure_pwrpol.yaml` -> `measure_pwrpol.py`
- `measure_basic_performance.yaml` -> `measure_basic_performance.py`
- `measure_full_performance.yaml` -> `measure_full_performance.py`
- `measure_hybrid.yaml` -> `measure_hybrid.py`
- `measure_hybrid_staircase.yaml` -> `measure_hybrid_staircase.py`
- `measure_vsweep.yaml` -> `measure_vsweep.py`
- `measure_pol_map.yaml` -> `measure_pol_map.py`
- `measure_pstatic.yaml` -> `measure_pstatic.py`
- `measure_pstatic_stability.yaml` -> `measure_pstatic_stability.py`
- `measure_chrono.yaml` -> `measure_chrono.py`
- `measure_repeating_dstep_chronop.yaml` -> `measure_repeating_dstep_chronop.py`
- `measure_repeating_gstep_chronop.yaml` -> `measure_repeating_gstep_chronop.py`
- `measure_repeating_hybrid.yaml` -> `measure_repeating_hybrid.py`
- `charge_hybrid.yaml` -> `charge_hybrid.py`
- `batt_hybrid_discharge_charge.yaml` -> `batt_hybrid_discharge-charge.py`
- `equilibrate.yaml` -> `equilibrate.py`
- `run_reduction.yaml` -> `run_reduction.py`

Run with:

```bash
python verify_potentiostat_experiment.py experiments/potentiostat/<workflow>.yaml --backend dry-run
```
