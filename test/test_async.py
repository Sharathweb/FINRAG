import asyncio
import uvicorn
from fastapi import FastAPI
from app.models.responses import ResponseFactory
from utils.utils import logger

app = FastAPI()

async def background_task():
    """
    Simulates an asynchronous I/O operation like file processing or 
    database updates.
    """
    try:
        # Simulate an asynchronous I/O operation
        await asyncio.sleep(1)
        logger.info("Background task executed successfully: Hello, World!")
    except Exception as e:
        logger.error(f"Error occurred during background task: {e}")

@app.get("/async-endpoint")
async def handle_async_request():
    logger.info("Received request for background task initiation.")
    
    # Use create_task to initiate the process without blocking the main event loop
    asyncio.create_task(background_task())
    
    # Return a standardized success response
    return ResponseFactory.success(
        data={"status": "Task initiated"},
        message="The background task has been started successfully."
    ).to_dict()

if __name__ == '__main__':
    # Use standard host and port configuration
    uvicorn.run(app, host="0.0.0.0", port=8001)