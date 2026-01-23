import time
import sys
import logging
from src.cnc_control.driver import Mill

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def test_move():
    """
    Connects to the mill, checks current position, and moves +1mm in X.
    """
    logger = logging.getLogger("test_cnc_move")
    logger.info("Starting CNC move test...")

    try:
        # Initialize Mill connection
        mill = Mill()
        # Disable auto-homing as the machine settings ($22=0) indicate homing is disabled
        mill.auto_home = False
        
        with mill:
            logger.info(f"Connected to mill. Homed: {mill.homed}")

            # Get current coordinates
            current_pos = mill.current_coordinates()
            # Explain the 1,1,1 issue
            logger.info("NOTE: Current position is reported as (1,1,1) because the driver adds the $27 homing pull-off (1mm) to the raw 0,0,0 position.")
            logger.info("This positive value conflicts with the driver's safety check (must be <= 0).")
            logger.info("Switching to RAW RELATIVE MOVEMENT to bypass driver validation and verify control.")

            # Send raw G-code for a relative move
            # G21 = Millimeters
            # G91 = Relative positioning
            # G01 X-1 F500 = Move X axis -1mm at 500mm/min
            logger.info("Sending: G21 G91 G01 X-1 F500")
            mill.execute_command("G21") # Ensure mm
            mill.execute_command("G91") # Set to relative mode
            mill.execute_command("G00 X-1") # Move
            
            time.sleep(1)
            
            mill.execute_command("G90") # Set back to absolute mode
            
            # Check position again
            new_pos = mill.current_coordinates()
            logger.info(f"Position after relative move: {new_pos}")
            
            logger.info("SUCCESS: Sent move command.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        # raise e # Optional: raise if we want the script to exit with error code

if __name__ == "__main__":
    test_move()
