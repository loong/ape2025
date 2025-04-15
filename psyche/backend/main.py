# Standard library imports
import asyncio
import base64
import datetime
import io
import logging
import os
import sys
import traceback
import uuid
from typing import Dict, Set

# Third-party imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import grpc
from PIL import Image
import uvicorn

# Local imports
from proto.sdxl_turbo_pb2 import Img2ImgBatchRequest
import proto.sdxl_turbo_pb2_grpc as pb2_grpc

# Constants
TEST_IMAGE_PATH = "../../seed-images/hanbok-red.jpg"
GRPC_SERVER_ADDRESS = "localhost:50051"
DEFAULT_PROMPT = "trade"
DEFAULT_FPS = 1.0
DEFAULT_NUM_IMAGES = 10
DEFAULT_NUM_GENERATED_IMAGES = 5
CONNECTION_LOG_INTERVAL = 60  # seconds
IMAGE_SEND_INTERVAL = 1.0  # seconds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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

# Store active connections per canvas
canvas_connections: Dict[str, Set[WebSocket]] = {
    "left-canva": set(),
    "right-canva": set()
}

# Add the SDXL-Turbo directory to the Python path
sdxl_turbo_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "models",
    "sdxl-turbo"
)
sys.path.append(sdxl_turbo_path)

# Initialize gRPC client
channel = grpc.insecure_channel(GRPC_SERVER_ADDRESS)
sdxl_client = pb2_grpc.SDXLTurboServiceStub(channel)

async def log_connections():
    """Periodically log the number of active connections per canvas."""
    while True:
        for canvas_slug, connections in canvas_connections.items():
            logger.info(
                f"Canvas '{canvas_slug}' has {len(connections)} active connections"
            )
        await asyncio.sleep(CONNECTION_LOG_INTERVAL)

@app.on_event("startup")
async def startup_event():
    """Start the connection logging task when the application starts."""
    asyncio.create_task(log_connections())
    logger.info("Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Handle server shutdown by closing all active WebSocket connections."""
    logger.info("Server shutting down")
    for canvas_slug, connections in canvas_connections.items():
        for connection in connections:
            try:
                await connection.close()
            except Exception as e:
                logger.error(
                    f"Error closing connection for canvas {canvas_slug}: {str(e)}"
                )

@app.websocket("/ws/{canvas_slug}")
async def websocket_endpoint(websocket: WebSocket, canvas_slug: str):
    """
    Handle WebSocket connections for a specific canvas.
    
    Args:
        websocket: The WebSocket connection
        canvas_slug: The identifier of the canvas to connect to
    """
    if canvas_slug not in canvas_connections:
        logger.error(f"Invalid canvas slug: {canvas_slug}")
        await websocket.close()
        return

    client_id = str(uuid.uuid4())[:8]  # Generate a short client ID for logging
    await websocket.accept()
    canvas_connections[canvas_slug].add(websocket)
    logger.info(
        f"New connection established for canvas '{canvas_slug}' "
        f"(Client ID: {client_id}). Total connections: {len(canvas_connections[canvas_slug])}"
    )
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally from canvas '{canvas_slug}'")
    except Exception as e:
        logger.error(
            f"Connection error for client {client_id} on canvas '{canvas_slug}': {str(e)}"
        )
        logger.error(f"Stack trace: {traceback.format_exc()}")
    finally:
        if websocket in canvas_connections[canvas_slug]:
            canvas_connections[canvas_slug].remove(websocket)
            logger.info(
                f"Connection closed for client {client_id} on canvas '{canvas_slug}'. "
                f"Remaining connections: {len(canvas_connections[canvas_slug])}"
            )

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
        
        logger.info(
            f"Image sent successfully to {successful_sends} clients on canvas '{canvas_slug}', "
            f"failed for {failed_sends} clients"
        )
        
    except Exception as e:
        logger.error(f"Error processing image for canvas '{canvas_slug}': {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")

@app.get("/test-stream/{canvas_slug}/{num_images}/{fps}")
async def test_stream(
    canvas_slug: str,
    num_images: int = DEFAULT_NUM_IMAGES,
    fps: float = DEFAULT_FPS
):
    """
    Test endpoint that streams a sequence of test images to a specific canvas.
    
    Args:
        canvas_slug: The canvas to stream images to
        num_images: Number of images to stream
        fps: Frames per second for streaming
    """
    if canvas_slug not in canvas_connections:
        return {"error": f"Invalid canvas slug: {canvas_slug}"}
        
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
            await send_image(img, canvas_slug)
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
    """
    Test endpoint that generates images using SDXL-Turbo and streams them to the right canvas.
    
    Args:
        prompt: The text prompt to use for image generation
        
    Returns:
        dict: Status of the inference operation
    """
    canvas_slug = "right-canva"
    if canvas_slug not in canvas_connections:
        return {"error": f"Invalid canvas slug: {canvas_slug}"}
        
    logger.info(f"Starting inference test with prompt: '{prompt}'")
    
    try:
        # Use the test image as input
        with open(TEST_IMAGE_PATH, 'rb') as f:
            image_bytes = f.read()
            
        # Send the test image to left-canva
        test_img = Image.open(TEST_IMAGE_PATH)
        await send_image(test_img, "left-canva")
        logger.info("Sent test image to left-canva")
        
        # Get test image dimensions for resizing
        test_width, test_height = test_img.size
        
        # Create batch request
        request = Img2ImgBatchRequest(
            image=image_bytes,
            prompt=prompt,
            num_images=DEFAULT_NUM_GENERATED_IMAGES,
            num_inference_steps=2,
            strength=0.8,
            guidance_scale=0.0
        )
        
        # Send request to SDXL-Turbo service
        response = sdxl_client.Img2ImgBatch(request)
        logger.info("Images generated successfully")
        
        # Stream generated images to canvas
        for i, image_bytes in enumerate(response.generated_images):
            try:
                # Convert bytes to PIL Image and resize
                img = Image.open(io.BytesIO(image_bytes))
                img = img.resize((test_width, test_height), Image.Resampling.LANCZOS)
                await send_image(img, canvas_slug)
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