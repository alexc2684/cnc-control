import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path so we can import src and the test script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cnc_control.mock import MockMill
from src.cnc_control.tools import Coordinates

class TestCNCMoveScript(unittest.TestCase):
    
    @patch('src.cnc_control.driver.Mill') # Patch the real Mill class where it is used or imported
    def test_cnc_move_logic(self, mock_mill_class):
        """
        Verifies that test_cnc_move.py performs the expected logic using a MockMill.
        """
        
        # Setup the mock instance to behave like our MockMill but with tracking
        # We can't directly use MockMill as the return value because we need to intercept calls
        # So we wrap or configure the MagicMock to behave sufficiently like Mill/MockMill
        
        # Instantiate our actual MockMill to define behavior
        real_mock_mill = MockMill()
        
        # Configure the mock class to return our real_mock_mill instance when instantiated
        mock_mill_class.return_value = real_mock_mill
        
        # Mock __enter__ to return self (standard context manager behavior)
        real_mock_mill.__enter__ = MagicMock(return_value=real_mock_mill)
        real_mock_mill.__exit__ = MagicMock(return_value=None)
        
        # Mock connect_to_mill to avoid resetting the serial connection
        # We want to keep the ser_mill instance we are about to configure
        real_mock_mill.connect_to_mill = MagicMock(return_value=real_mock_mill.ser_mill)

        # Spy on move_to_position to verify it was called with correct args
        real_mock_mill.move_to_position = MagicMock(wraps=real_mock_mill.move_to_position)
        
        # Set initial coordinates
        # MockSerialToMill inside MockMill maintains state.
        real_mock_mill.ser_mill.current_x = -10.0
        real_mock_mill.ser_mill.current_y = -20.0
        real_mock_mill.ser_mill.current_z = -5.0
        
        # Prevent auto-homing which resets coordinates
        real_mock_mill.homed = True
        
        print(f"Initial Mock Position: {real_mock_mill.current_coordinates()}")

        # Import the script function here to ensure patch is active
        # We might need to use run_path or importlib if it wasn't a module, 
        # but since I wrote it as a function `test_move`, I can import it.
        # However, direct import might fail if the file is at root and not in a package.
        # Let's try importing as a module since we added root to sys.path.
        import test_cnc_move
        
        # Run the test function
        test_cnc_move.test_move()
        
        # Verify interactions
        # 1. Check if move_to_position was called
        self.assertTrue(real_mock_mill.move_to_position.called, "move_to_position should have been called")
        
        # 2. Check arguments: Should be X=11.0, Y=20.0, Z=-5.0 (10.0 + 1.0)
        call_args = real_mock_mill.move_to_position.call_args
        # Only kwargs are guaranteed if called with kwargs, but let's check how it was called
        # The script uses kwargs: x_coordinate=target_x, ...
        kwargs = call_args.kwargs
        # Target X should be -10.0 + 1.0 = -9.0
        self.assertAlmostEqual(kwargs.get('x_coordinate'), -9.0, places=2)
        self.assertAlmostEqual(kwargs.get('y_coordinate'), -20.0, places=2)
        self.assertAlmostEqual(kwargs.get('z_coordinate'), -5.0, places=2)
        
        print("Verification passed!")

if __name__ == "__main__":
    unittest.main()
