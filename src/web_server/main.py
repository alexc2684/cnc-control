from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
import logging
import sys
import os

# Ensure the project root is in sys.path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_cnc_bounds import run_bounds_test, load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("web_server")

from pydantic import BaseModel

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="src/web_server/static"), name="static")

class MoveRequest(BaseModel):
    x: float
    y: float
    z: float

@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/index.html")

@app.post("/api/connect")
async def connect_and_test():
    """
    Trigger the CNC bounds test.
    """
    try:
        logger.info("Received request to run bounds test.")
        # We run the test synchronously for now as it blocks, but for a simple test this is fine.
        # In a real app, this should be a background task.
        run_bounds_test()
        return JSONResponse(content={"status": "success", "message": "Bounds test completed successfully."})
    except Exception as e:
        logger.error(f"Error running bounds test: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/move")
async def move_to_coordinates(request: MoveRequest):
    """
    Move the CNC machine to the specified coordinates.
    """
    config = load_config()
    x_max = -config["X_MAX"]
    y_max = -config["Y_MAX"]
    z_max = -config["Z_MAX"]

    # Bounds check
    if not (x_max <= request.x <= 0):
        raise HTTPException(status_code=400, detail=f"X coordinate {request.x} out of bounds ({x_max} to 0)")
    if not (y_max <= request.y <= 0):
        raise HTTPException(status_code=400, detail=f"Y coordinate {request.y} out of bounds ({y_max} to 0)")
    if not (z_max <= request.z <= 0):
        raise HTTPException(status_code=400, detail=f"Z coordinate {request.z} out of bounds ({z_max} to 0)")

    try:
        from src.cnc_control.driver import Mill
        mill = Mill()
        mill.auto_home = False # Assume already homed or zeroed

        with mill:
            logger.info(f"Moving to X={request.x}, Y={request.y}, Z={request.z}")
            mill.execute_command("G21") # MM
            mill.execute_command("G90") # Absolute
            
            # Move in sequence or all at once? All at once is fine for G01
            command = f"G01 X{request.x} Y{request.y} Z{request.z} F{config['FEED_RATE']}"
            mill.execute_command(command)
            # Wait for completion implemented in execute_command via wait_for_completion somewhat, 
            # but let's add a small dwell or rely on driver synchronous behavior.
            
            return JSONResponse(content={"status": "success", "message": f"Moved to ({request.x}, {request.y}, {request.z})"})
            
    except Exception as e:
        logger.error(f"Error executing move: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
