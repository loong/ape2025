"""SDXL-Turbo inference client for image generation."""

import logging
import os
import sys
from typing import List

import grpc
from PIL import Image
import io
import traceback

from config import (
    GRPC_SERVER_ADDRESS,
    DEFAULT_NUM_GENERATED_IMAGES,
    TEST_IMAGE_PATH
)

# Add the SDXL-Turbo directory to the Python path
sdxl_turbo_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "models",
    "sdxl-turbo"
)
sys.path.append(sdxl_turbo_path)

# Now we can import the proto files
from proto.sdxl_turbo_pb2 import Img2ImgBatchRequest
import proto.sdxl_turbo_pb2_grpc as pb2_grpc

logger = logging.getLogger(__name__)

class InferenceClient:
    """Client for interacting with the SDXL-Turbo service."""
    
    def __init__(self):
        """Initialize the inference client."""
        self.channel = grpc.insecure_channel(GRPC_SERVER_ADDRESS)
        self.client = pb2_grpc.SDXLTurboServiceStub(self.channel)
        logger.info("Inference client initialized")

    def generate_images(
        self,
        prompt: str,
        num_images: int = DEFAULT_NUM_GENERATED_IMAGES,
        strength: float = 0.8,
        guidance_scale: float = 0.0
    ) -> List[Image.Image]:
        """Generate images using SDXL-Turbo.
        
        Args:
            prompt: The text prompt for image generation
            num_images: Number of images to generate
            strength: Strength parameter for img2img
            guidance_scale: Guidance scale parameter
            
        Returns:
            List[Image.Image]: List of generated images
        """
        try:
            # Read the test image
            with open(TEST_IMAGE_PATH, 'rb') as f:
                image_bytes = f.read()
            
            # Create batch request
            request = Img2ImgBatchRequest(
                image=image_bytes,
                prompt=prompt,
                num_images=num_images,
                num_inference_steps=2,
                strength=strength,
                guidance_scale=guidance_scale
            )
            
            # Send request to SDXL-Turbo service
            response = self.client.Img2ImgBatch(request)
            logger.info("Images generated successfully")
            
            # Convert response to PIL Images
            images = []
            for image_bytes in response.generated_images:
                img = Image.open(io.BytesIO(image_bytes))
                images.append(img)
            
            return images
            
        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise

    def close(self):
        """Close the gRPC channel."""
        self.channel.close()
        logger.info("Inference client closed") 