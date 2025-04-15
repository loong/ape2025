"""Image handling and processing functionality."""

import base64
import datetime
import io
import logging
import uuid
from typing import Set

from PIL import Image
from fastapi import WebSocket

from config import IMAGE_SEND_INTERVAL

logger = logging.getLogger(__name__)

class ImageHandler:
    """Handles image processing and sending to WebSocket clients."""
    
    @staticmethod
    async def send_image(img: Image.Image, connections: Set[WebSocket], canvas_slug: str):
        """Send a PIL Image to all connected clients of a specific canvas.
        
        Args:
            img: A PIL Image object to send
            connections: Set of WebSocket connections to send to
            canvas_slug: The slug of the canvas to send the image to
        """
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

    @staticmethod
    def resize_image(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """Resize an image to target dimensions.
        
        Args:
            img: The image to resize
            target_width: Target width in pixels
            target_height: Target height in pixels
            
        Returns:
            Image.Image: The resized image
        """
        return img.resize((target_width, target_height), Image.Resampling.LANCZOS) 