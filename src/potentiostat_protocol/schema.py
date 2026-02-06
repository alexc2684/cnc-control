from __future__ import annotations

from typing import Any, Dict, Literal, Optional

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


WORKFLOW_NAMES = (
    "measure_ocp",
    "measure_eis",
    "measure_ocp_eis",
    "measure_pwrpol",
    "measure_basic_performance",
    "measure_full_performance",
    "measure_hybrid",
    "measure_hybrid_staircase",
    "measure_vsweep",
    "measure_pol_map",
    "measure_pstatic",
    "measure_pstatic_stability",
    "measure_chrono",
    "measure_repeating_dstep_chronop",
    "measure_repeating_gstep_chronop",
    "measure_repeating_hybrid",
    "charge_hybrid",
    "batt_hybrid_discharge_charge",
    "equilibrate",
    "run_reduction",
)

WorkflowName = Literal[
    "measure_ocp",
    "measure_eis",
    "measure_ocp_eis",
    "measure_pwrpol",
    "measure_basic_performance",
    "measure_full_performance",
    "measure_hybrid",
    "measure_hybrid_staircase",
    "measure_vsweep",
    "measure_pol_map",
    "measure_pstatic",
    "measure_pstatic_stability",
    "measure_chrono",
    "measure_repeating_dstep_chronop",
    "measure_repeating_gstep_chronop",
    "measure_repeating_hybrid",
    "charge_hybrid",
    "batt_hybrid_discharge_charge",
    "equilibrate",
    "run_reduction",
]

_REQUIRED_PARAMETERS = {
    "run_reduction": {"reduction_config_file"},
}


def _normalize_param_key(name: str) -> str:
    return name.strip().replace("-", "_").lower()


class RuntimeConfig(BaseModel):
    data_path: str = "."
    file_suffix: str = "Experiment"
    exp_notes: str = ""
    num_loops: int = 1
    kst_path: Optional[str] = None
    show_plot: bool = False

    @field_validator("num_loops")
    @classmethod
    def _validate_num_loops(cls, value: int) -> int:
        if value < 1:
            raise ValueError("num_loops must be >= 1")
        return value


class PotentiostatExperiment(BaseModel):
    name: str
    workflow: WorkflowName
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    parameters: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _normalize_parameters(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        raw_params = values.get("parameters", {}) or {}
        normalized = {}
        for key, value in raw_params.items():
            normalized[_normalize_param_key(str(key))] = value
        values["parameters"] = normalized
        return values

    @model_validator(mode="after")
    def _validate_required_parameters(self) -> "PotentiostatExperiment":
        workflow = self.workflow
        parameters = self.parameters
        required = _REQUIRED_PARAMETERS.get(workflow, set())
        missing = sorted(required.difference(parameters.keys()))
        if missing:
            missing_text = ", ".join(missing)
            raise ValueError(
                f"Workflow '{workflow}' is missing required parameters: {missing_text}"
            )
        return self

    @classmethod
    def from_yaml(cls, path: str) -> "PotentiostatExperiment":
        with open(path, "r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        return cls(**payload)

    def parameter(self, name: str, default: Any = None) -> Any:
        return self.parameters.get(_normalize_param_key(name), default)
