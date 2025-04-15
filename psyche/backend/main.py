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

# Store active connections
connections = []

async def log_connections():
    """Periodically log the number of active connections"""
    while True:
        logger.info(f"Active connections: {len(connections)}")
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
    for connection in connections:
        try:
            await connection.close()
        except Exception as e:
            logger.error(f"Error closing connection during shutdown: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())[:8]  # Generate a short client ID for logging
    await websocket.accept()
    connections.append(websocket)
    logger.info(f"New connection established (Client ID: {client_id}). Total connections: {len(connections)}")
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"Connection error for client {client_id}: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
    finally:
        if websocket in connections:
            connections.remove(websocket)
            logger.info(f"Connection closed for client {client_id}. Remaining connections: {len(connections)}")

async def send_image(img: Image.Image):
    """
    Send a PIL Image to all connected clients.
    
    Args:
        img: A PIL Image object to send
    """
    if not connections:
        logger.debug("No active connections, skipping image send")
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
        
        for connection in connections[:]:  # Create a copy of the list to safely modify it
            try:
                await connection.send_json(message)
                successful_sends += 1
            except Exception as e:
                logger.error(f"Failed to send image to client: {str(e)}")
                failed_sends += 1
                if connection in connections:
                    connections.remove(connection)
        
        logger.info(f"Image sent successfully to {successful_sends} clients, failed for {failed_sends} clients")
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")

@app.get("/test-stream/{num_images}/{fps}")
async def test_stream(num_images: int = 10, fps: float = 1.0):
    """
    Test endpoint that streams a sequence of test images.
    """
    logger.info(f"Starting test stream: {num_images} images at {fps} FPS")
    sleep_time = 1.0 / fps
    
    for i in range(num_images):
        try:
            # This would use actual images in production
            test_image_path = f"test_images/image_{i}.jpg"
            logger.debug(f"Sending image {i+1}/{num_images}: {test_image_path}")
            img = Image.open(test_image_path)
            await send_image(img)
            await asyncio.sleep(sleep_time)
        except Exception as e:
            logger.error(f"Error in test stream iteration {i}: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
    
    logger.info("Test stream completed")
    return {"status": "complete"}

if __name__ == "__main__":
    # Create test_images directory if it doesn't exist
    os.makedirs("test_images", exist_ok=True)
    logger.info("Starting server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 