import sys
import os
import time

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from cnc_control.driver import Mill
from cnc_control.exceptions import MillConnectionError

def main():
    print("Starting CNC Control...")
    try:
        with Mill() as mill:
            print(f"Connected to mill: {mill.active_connection}")
            print("Current Status:", mill.current_status())
            
            # Example movement (interactive or safe)
            # mill.home()
            
    except MillConnectionError as e:
        print(f"Could not connect to mill: {e}")
        print("Note: If no hardware is connected, this is expected unless using a mock.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
