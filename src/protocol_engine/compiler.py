from typing import List, Dict, Any
from pydantic import BaseModel
from src.protocol_engine.schema import ExperimentSequence, MoveAction, ImageAction
from src.protocol_engine.config import DeckConfig, CoordinateModel
from src.protocol_engine.path_planner import PathPlanner

class ProtocolStep(BaseModel):
    """A single executable step in the protocol."""
    type: str  # "move", "image"
    parameters: Dict[str, Any]

class CompiledProtocol(BaseModel):
    """A complete compiled protocol ready for execution."""
    steps: List[ProtocolStep]

class Compiler:
    """
    Compiles an ExperimentSequence into a safe CompiledProtocol.
    """
    def __init__(self, config: DeckConfig):
        self.config = config
        self.planner = PathPlanner(config)
        
    def compile(self, sequence: ExperimentSequence) -> CompiledProtocol:
        steps = []
        
        # Start simulation at Home
        if "home" in self.config.locations:
            current_pos = self.config.locations["home"]
        else:
            # Fallback if home is not defined, though configuration suggests it should be
            current_pos = CoordinateModel(x=0.0, y=0.0, z=0.0)

        for action in sequence.actions:
            if action.action_type == "move":
                target_name = action.target_location
                try:
                    target_base = self.config.locations[target_name]
                except KeyError:
                    raise ValueError(f"Unknown location for move action: {target_name}")
                
                # Apply Z offset
                target_pos = CoordinateModel(
                    x=target_base.x,
                    y=target_base.y,
                    z=target_base.z + action.z_offset
                )
                
                # Plan path
                plan = self.planner.plan_path(current_pos, target_pos)
                
                # Convert waypoints to steps
                for wp in plan.waypoints:
                    steps.append(ProtocolStep(
                        type="move", 
                        parameters={"x": wp.x, "y": wp.y, "z": wp.z}
                    ))
                
                current_pos = target_pos
                
            elif action.action_type == "image":
                target_name = action.target_location
                try:
                    target_base = self.config.locations[target_name]
                except KeyError:
                    raise ValueError(f"Unknown location for image action: {target_name}")
                
                # Plan move to target
                target_pos = target_base # No offset for image unless specified? Assume target is ideal imaging spot.
                
                plan = self.planner.plan_path(current_pos, target_pos)
                
                for wp in plan.waypoints:
                    steps.append(ProtocolStep(
                        type="move",
                        parameters={"x": wp.x, "y": wp.y, "z": wp.z}
                    ))
                
                # Add image capture step
                steps.append(ProtocolStep(
                    type="image",
                    parameters={"label": action.label, "location": target_name}
                ))
                
                current_pos = target_pos

        return CompiledProtocol(steps=steps)
