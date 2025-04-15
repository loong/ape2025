from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image
import io
import base64
import datetime
import asyncio
import uuid
import os
import logging
import traceback
from typing import Dict, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections per canvas
canvas_connections: Dict[str, Set[WebSocket]] = {
    "left-canva": set(),
    "right-canva": set()
}

async def log_connections():
    """Periodically log the number of active connections per canvas"""
    while True:
        for canvas_slug, connections in canvas_connections.items():
            logger.info(f"Canvas '{canvas_slug}' has {len(connections)} active connections")
        await asyncio.sleep(60)  # Log every minute

@app.on_event("startup")
async def startup_event():
    """Start the connection logging task when the application starts"""
    asyncio.create_task(log_connections())
    logger.info("Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Handle server shutdown"""
    logger.info("Server shutting down")
    for canvas_slug, connections in canvas_connections.items():
        for connection in connections:
            try:
                await connection.close()
            except Exception as e:
                logger.error(f"Error closing connection for canvas {canvas_slug}: {str(e)}")

@app.websocket("/ws/{canvas_slug}")
async def websocket_endpoint(websocket: WebSocket, canvas_slug: str):
    if canvas_slug not in canvas_connections:
        logger.error(f"Invalid canvas slug: {canvas_slug}")
        await websocket.close()
        return

    client_id = str(uuid.uuid4())[:8]  # Generate a short client ID for logging
    await websocket.accept()
    canvas_connections[canvas_slug].add(websocket)
    logger.info(f"New connection established for canvas '{canvas_slug}' (Client ID: {client_id}). Total connections: {len(canvas_connections[canvas_slug])}")
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally from canvas '{canvas_slug}'")
    except Exception as e:
        logger.error(f"Connection error for client {client_id} on canvas '{canvas_slug}': {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
    finally:
        if websocket in canvas_connections[canvas_slug]:
            canvas_connections[canvas_slug].remove(websocket)
            logger.info(f"Connection closed for client {client_id} on canvas '{canvas_slug}'. Remaining connections: {len(canvas_connections[canvas_slug])}")

async def send_image(img: Image.Image, canvas_slug: str):
    """
    Send a PIL Image to all connected clients of a specific canvas.
    
    Args:
        img: A PIL Image object to send
        canvas_slug: The slug of the canvas to send the image to
    """
    if canvas_slug not in canvas_connections:
        logger.error(f"Invalid canvas slug: {canvas_slug}")
        return
        
    connections = canvas_connections[canvas_slug]
    if not connections:
        logger.debug(f"No active connections for canvas '{canvas_slug}', skipping image send")
        return
    
    try:
        # Process the image
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Create the message
        message = {
            "timestamp": datetime.datetime.now().isoformat(),
            "image": img_str,
            "image_id": str(uuid.uuid4())
        }
        
        # Send to all clients
        successful_sends = 0
        failed_sends = 0
        
        for connection in list(connections):  # Create a copy of the set to safely modify it
            try:
                await connection.send_json(message)
                successful_sends += 1
            except Exception as e:
                logger.error(f"Failed to send image to client on canvas '{canvas_slug}': {str(e)}")
                failed_sends += 1
                if connection in connections:
                    connections.remove(connection)
        
        logger.info(f"Image sent successfully to {successful_sends} clients on canvas '{canvas_slug}', failed for {failed_sends} clients")
        
    except Exception as e:
        logger.error(f"Error processing image for canvas '{canvas_slug}': {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")

@app.get("/test-stream/{canvas_slug}/{num_images}/{fps}")
async def test_stream(canvas_slug: str, num_images: int = 10, fps: float = 1.0):
    """
    Test endpoint that streams a sequence of test images to a specific canvas.
    """
    if canvas_slug not in canvas_connections:
        return {"error": f"Invalid canvas slug: {canvas_slug}"}
        
    logger.info(f"Starting test stream for canvas '{canvas_slug}': {num_images} images at {fps} FPS")
    sleep_time = 1.0 / fps
    
    for i in range(num_images):
        try:
            # This would use actual images in production
            test_image_path = f"test_images/image_{i}.jpg"
            logger.debug(f"Sending image {i+1}/{num_images} to canvas '{canvas_slug}': {test_image_path}")
            img = Image.open(test_image_path)
            await send_image(img, canvas_slug)
            await asyncio.sleep(sleep_time)
        except Exception as e:
            logger.error(f"Error in test stream iteration {i} for canvas '{canvas_slug}': {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
    
    logger.info(f"Test stream completed for canvas '{canvas_slug}'")
    return {"status": "complete"}

if __name__ == "__main__":
    # Create test_images directory if it doesn't exist
    os.makedirs("test_images", exist_ok=True)
    logger.info("Starting server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 