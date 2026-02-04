from typing import List, Optional
from pydantic import BaseModel, ValidationError
from src.protocol_engine.config import DeckConfig, CoordinateModel

class PathPlan(BaseModel):
    """Encapsulates a sequence of waypoints for movement."""
    waypoints: List[CoordinateModel]
    estimated_duration: Optional[float] = None

class PathPlanner:
    """
    Validates positions and generates safe paths for the CNC mill.
    """
    def __init__(self, config: DeckConfig):
        self.config = config

    def validate_bounds(self, coord: CoordinateModel):
        """
        Check if the coordinate is within the machine bounds.
        Raises ValueError if out of bounds.
        """
        bounds = self.config.machine_bounds
        
        if not (bounds.x_min <= coord.x <= bounds.x_max):
            raise ValueError(f"X coordinate {coord.x} out of bounds [{bounds.x_min}, {bounds.x_max}]")
        if not (bounds.y_min <= coord.y <= bounds.y_max):
            raise ValueError(f"Y coordinate {coord.y} out of bounds [{bounds.y_min}, {bounds.y_max}]")
        if not (bounds.z_min <= coord.z <= bounds.z_max):
            raise ValueError(f"Z coordinate {coord.z} out of bounds [{bounds.z_min}, {bounds.z_max}]")

    def plan_path(self, start: CoordinateModel, end: CoordinateModel) -> PathPlan:
        """
        Generate a safe path from start to end using a lift-travel-lower strategy.
        Optimized to avoid redundant moves.
        """
        safe_z = self.config.safe_z_height
        waypoints = []

        # Check if we are already at the exact target location
        if start.x == end.x and start.y == end.y and start.z == end.z:
            return PathPlan(waypoints=[])

        # 1. Lift logic
        # Only lift if we are moving in XY, OR if we need to go UP to reach the target Z (and not colliding)
        # Simplified: If moving XY, lift to safe Z.
        moving_xy = (start.x != end.x or start.y != end.y)
        
        current_z = start.z
        
        if moving_xy:
            # If we are below safe height (lower value), lift.
            # Assuming Z moves up as it gets closer to 0 or positive.
            # Safe Z is usually highest travel plane.
            if start.z < safe_z:
                waypoint_lift = CoordinateModel(x=start.x, y=start.y, z=safe_z)
                waypoints.append(waypoint_lift)
                current_z = safe_z
            
            # 2. Travel to target XY at safe Z (or current Z if already safe/high)
            waypoint_travel = CoordinateModel(x=end.x, y=end.y, z=current_z)
            waypoints.append(waypoint_travel)
            
        # 3. Lower/Move to target Z
        if current_z != end.z:
            waypoint_lower = CoordinateModel(x=end.x, y=end.y, z=end.z)
            waypoints.append(waypoint_lower)
            
        # 4. Catch-all for purely vertical move that didn't trigger XY logic
        if not moving_xy and not waypoints and start.z != end.z:
             waypoints.append(CoordinateModel(x=end.x, y=end.y, z=end.z))
        
        return PathPlan(waypoints=waypoints)
