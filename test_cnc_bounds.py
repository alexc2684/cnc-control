import os
import sys
import time
import logging
from dotenv import load_dotenv
from src.cnc_control.driver import Mill

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("test_cnc_bounds")

def load_config():
    """Load configuration from .env file."""
    load_dotenv()
    print(os.getenv("CNC_X_MAX_MM"))
    
    config = {
        "X_MAX": float(os.getenv("CNC_X_MAX_MM", 10.0)),
        "Y_MAX": float(os.getenv("CNC_Y_MAX_MM", 10.0)),
        "Z_MAX": float(os.getenv("CNC_Z_MAX_MM", 10.0)),
        "FEED_RATE": int(os.getenv("CNC_FEED_RATE", 500))
    }
    return config

def run_bounds_test():
    """
    Reads bounds from .env and moves the CNC machine.
    Assumes machine is at origin (0,0,0) and max travel is in negative direction.
    """
    config = load_config()
    logger.info(f"Loaded Configuration: {config}")
    
    logger.info("Starting CNC Bounds Test...")
    logger.info("WARNING: This script assumes the machine is currently at the Origin (0,0,0).")
    logger.info("WARNING: Machine will move to negative coordinates based on the .env file.")

    try:
        mill = Mill()
        # Disable auto-home as per previous scripts/user setup
        mill.auto_home = False
        
        with mill:
            logger.info("Connected to mill.")
            
            # 1. Set Absolute Distance Mode (G90) and Units to MM (G21)
            logger.info("Setting Absolute Mode (G90) and MM (G21)...")
            mill.execute_command("G21")
            mill.execute_command("G90")

            # 2. X Axis Test
            x_target = -config["X_MAX"]
            logger.info(f"--- Testing X Axis: Moving to {x_target} ---")
            mill.execute_command(f"G01 X{x_target} F{config['FEED_RATE']}")
            mill.execute_command("G4 P0.5") # Dwell 0.5s
            
            logger.info("Returning X to 0...")
            mill.execute_command(f"G01 X0 F{config['FEED_RATE']}")
            mill.execute_command("G4 P0.5")

            # 3. Y Axis Test
            y_target = -config["Y_MAX"]
            logger.info(f"--- Testing Y Axis: Moving to {y_target} ---")
            mill.execute_command(f"G01 Y{y_target} F{config['FEED_RATE']}")
            mill.execute_command("G4 P0.5")

            logger.info("Returning Y to 0...")
            mill.execute_command(f"G01 Y0 F{config['FEED_RATE']}")
            mill.execute_command("G4 P0.5")

            # 4. Z Axis Test
            z_target = -config["Z_MAX"]
            logger.info(f"--- Testing Z Axis: Moving to {z_target} ---")
            mill.execute_command(f"G01 Z{z_target} F{config['FEED_RATE']}")
            mill.execute_command("G4 P0.5")

            logger.info("Returning Z to 0...")
            mill.execute_command(f"G01 Z0 F{config['FEED_RATE']}")
            mill.execute_command("G4 P0.5")
            
            logger.info("Bounds test completed successfully.")
            
    except Exception as e:
        logger.error(f"An error occurred during the test: {e}")
        raise

if __name__ == "__main__":
    run_bounds_test()
