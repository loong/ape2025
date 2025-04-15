import grpc
import argparse
from PIL import Image
import io

import proto.sdxl_turbo_pb2 as pb2
import proto.sdxl_turbo_pb2_grpc as pb2_grpc

def image_to_bytes(image_path: str) -> bytes:
    """Convert image file to bytes."""
    with open(image_path, 'rb') as f:
        return f.read()

def bytes_to_image(image_bytes: bytes, output_path: str):
    """Save bytes as image file."""
    with open(output_path, 'wb') as f:
        f.write(image_bytes)

def run_single_image(client, image_path: str, prompt: str, output_path: str):
    """Generate a single image."""
    # Convert image to bytes
    image_bytes = image_to_bytes(image_path)
    
    # Create request
    request = pb2.Img2ImgRequest(
        image=image_bytes,
        prompt=prompt,
        num_inference_steps=2,
        strength=0.8,
        guidance_scale=0.0,
        seed=0  # Set a default seed value
    )
    
    # Send request
    response = client.Img2Img(request)
    
    # Save result
    bytes_to_image(response.generated_image, output_path)
    print(f"Image generated and saved to {output_path}")
    print(f"Request ID: {response.request_id}")
    print(f"Processing time: {response.processing_time_ms}ms")

def run_batch(client, image_path: str, prompt: str, num_images: int, output_prefix: str):
    """Generate multiple images."""
    # Convert image to bytes
    image_bytes = image_to_bytes(image_path)
    
    # Create request
    request = pb2.Img2ImgBatchRequest(
        image=image_bytes,
        prompt=prompt,
        num_images=num_images,
        num_inference_steps=2,
        strength=0.8,
        guidance_scale=0.0
    )
    
    # Send request
    response = client.Img2ImgBatch(request)
    
    # Save results
    for i, image_bytes in enumerate(response.generated_images):
        output_path = f"{output_prefix}_{i}.png"
        bytes_to_image(image_bytes, output_path)
        print(f"Image {i} saved to {output_path}")
    
    print(f"Request ID: {response.request_id}")
    print(f"Processing time: {response.processing_time_ms}ms")

def check_queue_status(client):
    """Check current queue status."""
    request = pb2.QueueStatusRequest()
    response = client.GetQueueStatus(request)
    print(f"Queue length: {response.queue_length}")
    print(f"Estimated wait time: {response.estimated_wait_time_ms}ms")
    print(f"Active requests: {response.active_requests}")

def main():
    parser = argparse.ArgumentParser(description="SDXL-Turbo gRPC Client")
    parser.add_argument("--mode", choices=["single", "batch", "status"], required=True,
                      help="Operation mode: single image, batch, or status check")
    parser.add_argument("--image", help="Input image path")
    parser.add_argument("--prompt", help="Generation prompt")
    parser.add_argument("--output", help="Output path (for single mode) or prefix (for batch mode)")
    parser.add_argument("--num-images", type=int, help="Number of images to generate (batch mode)")
    
    args = parser.parse_args()
    
    # Create channel and client
    channel = grpc.insecure_channel('localhost:50051')
    client = pb2_grpc.SDXLTurboServiceStub(channel)
    
    if args.mode == "status":
        check_queue_status(client)
    elif args.mode == "single":
        if not all([args.image, args.prompt, args.output]):
            parser.error("--image, --prompt, and --output are required for single mode")
        run_single_image(client, args.image, args.prompt, args.output)
    elif args.mode == "batch":
        if not all([args.image, args.prompt, args.output, args.num_images]):
            parser.error("--image, --prompt, --output, and --num-images are required for batch mode")
        run_batch(client, args.image, args.prompt, args.num_images, args.output)

if __name__ == '__main__':
    main() 