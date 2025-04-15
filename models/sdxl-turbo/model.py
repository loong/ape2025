import torch
from diffusers import AutoPipelineForImage2Image
from PIL import Image
import io
import time
import logging

class SDXLTurboModel:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.logger.info(f"Using device: {self.device}")
        
        # Load the model
        self.pipeline = AutoPipelineForImage2Image.from_pretrained(
            "stabilityai/sdxl-turbo",
            torch_dtype=torch.float16,
            variant="fp16"
        )
        self.pipeline = self.pipeline.to(self.device)
        self.logger.info("Model loaded successfully")

    def _bytes_to_image(self, image_bytes: bytes) -> Image.Image:
        """Convert bytes to PIL Image."""
        return Image.open(io.BytesIO(image_bytes))

    def _image_to_bytes(self, image: Image.Image) -> bytes:
        """Convert PIL Image to bytes."""
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    def generate_image(self, 
                      image_bytes: bytes,
                      prompt: str,
                      num_inference_steps: int = 2,
                      strength: float = 0.8,
                      guidance_scale: float = 0.0,
                      seed: int = 0) -> bytes:
        """Generate a single image."""
        start_time = time.time()
        
        try:
            # Convert input image
            init_image = self._bytes_to_image(image_bytes)
            init_image = init_image.resize((512, 512))
            
            # Set up generator with seed
            generator = torch.Generator(device=self.device).manual_seed(seed)
            
            # Generate image
            result = self.pipeline(
                prompt=prompt,
                image=init_image,
                num_inference_steps=num_inference_steps,
                strength=strength,
                guidance_scale=guidance_scale,
                generator=generator
            ).images[0]
            
            # Convert to bytes
            return self._image_to_bytes(result)
        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            raise

    def generate_batch(self,
                      image_bytes: bytes,
                      prompt: str,
                      num_images: int,
                      num_inference_steps: int = 2,
                      strength: float = 0.8,
                      guidance_scale: float = 0.0,
                      seed: int = 0) -> list[bytes]:
        """Generate multiple images."""
        start_time = time.time()
        
        try:
            # Convert input image
            init_image = self._bytes_to_image(image_bytes)
            init_image = init_image.resize((512, 512))
            
            # Set up generator with seed
            generator = torch.Generator(device=self.device).manual_seed(seed)
            
            # Generate images
            results = self.pipeline(
                prompt=prompt,
                image=init_image,
                num_inference_steps=num_inference_steps,
                strength=strength,
                guidance_scale=guidance_scale,
                generator=generator,
                num_images_per_prompt=num_images
            ).images
            
            # Convert to bytes
            return [self._image_to_bytes(img) for img in results]
        except Exception as e:
            self.logger.error(f"Error generating batch: {str(e)}")
            raise 