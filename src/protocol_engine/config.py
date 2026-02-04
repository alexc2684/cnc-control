from typing import Dict, Optional
from pydantic import BaseModel, root_validator
import yaml
from pathlib import Path

# We can reuse the Coordinates concept but as a Pydantic model for validation
class CoordinateModel(BaseModel):
    x: float
    y: float
    z: float

class MachineBounds(BaseModel):
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float

class DeckConfig(BaseModel):
    machine_bounds: MachineBounds
    safe_z_height: float
    locations: Dict[str, CoordinateModel]
    homing_enabled: bool = True
    camera_source: int = 0
    serial_port: Optional[str] = None

    @classmethod
    def from_yaml(cls, path: str) -> "DeckConfig":
        """Load configuration from a YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)
