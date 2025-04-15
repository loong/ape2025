"""Main application entry point."""

import asyncio
import logging
import os
import sys
import traceback

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image

from config import (
    LOGGING_CONFIG,
    TEST_IMAGE_PATH,
    DEFAULT_PROMPT,
    DEFAULT_FPS,
    DEFAULT_NUM_IMAGES,
    DEFAULT_NUM_GENERATED_IMAGES,
    IMAGE_SEND_INTERVAL
)
from websocket_manager import WebSocketManager
from image_handler import ImageHandler
from inference_client import InferenceClient

# Configure logging
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
ws_manager = WebSocketManager()
inference_client = InferenceClient()

@app.on_event("startup")
async def startup_event():
    """Start the application and initialize managers."""
    await ws_manager.start()
    logger.info("Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Handle server shutdown."""
    await ws_manager.stop()
    inference_client.close()
    logger.info("Server shutting down")

@app.websocket("/ws/{canvas_slug}")
async def websocket_endpoint(websocket: WebSocket, canvas_slug: str):
    """Handle WebSocket connections."""
    if not await ws_manager.connect(websocket, canvas_slug):
        return

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"Client disconnected normally from canvas '{canvas_slug}'")
    except Exception as e:
        logger.error(f"Connection error for canvas '{canvas_slug}': {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
    finally:
        await ws_manager.disconnect(websocket, canvas_slug)

@app.get("/test-stream/{canvas_slug}/{num_images}/{fps}")
async def test_stream(
    canvas_slug: str,
    num_images: int = DEFAULT_NUM_IMAGES,
    fps: float = DEFAULT_FPS
):
    """Test endpoint that streams a sequence of test images to a specific canvas."""
    connections = ws_manager.get_connections(canvas_slug)
    if not connections:
        return {"error": f"No active connections for canvas '{canvas_slug}'"}
        
    logger.info(
        f"Starting test stream for canvas '{canvas_slug}': "
        f"{num_images} images at {fps} FPS"
    )
    sleep_time = 1.0 / fps
    
    for i in range(num_images):
        try:
            test_image_path = f"test_images/image_{i}.jpg"
            logger.debug(
                f"Sending image {i+1}/{num_images} to canvas '{canvas_slug}': "
                f"{test_image_path}"
            )
            img = Image.open(test_image_path)
            await ImageHandler.send_image(img, connections, canvas_slug)
            await asyncio.sleep(sleep_time)
        except Exception as e:
            logger.error(
                f"Error in test stream iteration {i} for canvas '{canvas_slug}': {str(e)}"
            )
            logger.error(f"Stack trace: {traceback.format_exc()}")
    
    logger.info(f"Test stream completed for canvas '{canvas_slug}'")
    return {"status": "complete"}

@app.get("/test-inference")
async def test_inference(prompt: str = DEFAULT_PROMPT):
    """Test endpoint that generates images using SDXL-Turbo."""
    left_connections = ws_manager.get_connections("left-canva")
    right_connections = ws_manager.get_connections("right-canva")
    
    if not right_connections:
        return {"error": "No active connections for right canvas"}
        
    logger.info(f"Starting inference test with prompt: '{prompt}'")
    
    try:
        # Send the test image to left-canva
        test_img = Image.open(TEST_IMAGE_PATH)
        await ImageHandler.send_image(test_img, left_connections, "left-canva")
        logger.info("Sent test image to left-canva")
        
        # Get test image dimensions for resizing
        test_width, test_height = test_img.size
        
        # Generate images
        images = inference_client.generate_images(prompt)
        
        # Stream generated images to right-canva
        for i, img in enumerate(images):
            try:
                # Resize image to match test image dimensions
                img = ImageHandler.resize_image(img, test_width, test_height)
                await ImageHandler.send_image(img, right_connections, "right-canva")
                logger.debug(f"Sent image {i+1}/{DEFAULT_NUM_GENERATED_IMAGES}")
                await asyncio.sleep(IMAGE_SEND_INTERVAL)
            except Exception as e:
                logger.error(f"Error processing image {i+1}: {str(e)}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                
    except Exception as e:
        logger.error(f"Error in inference: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
    
    logger.info("Inference test completed")
    return {"status": "complete"}

if __name__ == "__main__":
    # Create test_images directory if it doesn't exist
    os.makedirs("test_images", exist_ok=True)
    logger.info("Starting server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 