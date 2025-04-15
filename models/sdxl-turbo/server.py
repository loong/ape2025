import asyncio
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import List

import grpc
from grpc import aio

from model import SDXLTurboModel
import proto.sdxl_turbo_pb2 as pb2
import proto.sdxl_turbo_pb2_grpc as pb2_grpc

class RequestQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.active_requests = 0
        self.avg_processing_time = 0
        self.total_processed = 0

    async def add_request(self, request_id: str, request_data: dict):
        await self.queue.put((request_id, request_data))

    async def get_request(self):
        return await self.queue.get()

    def update_processing_time(self, processing_time_ms: int):
        self.total_processed += 1
        self.avg_processing_time = (
            (self.avg_processing_time * (self.total_processed - 1) + processing_time_ms)
            / self.total_processed
        )

    def get_status(self):
        return {
            "queue_length": self.queue.qsize(),
            "active_requests": self.active_requests,
            "estimated_wait_time_ms": self.avg_processing_time * self.queue.qsize()
        }

class SDXLTurboServicer(pb2_grpc.SDXLTurboServiceServicer):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = SDXLTurboModel()
        self.request_queue = RequestQueue()
        self.executor = ThreadPoolExecutor(max_workers=1)  # Single worker for MPS
        self.request_counter = 0  # Add a counter for request IDs
        self.logger.info("SDXL-Turbo servicer initialized")

    async def Img2Img(self, request: pb2.Img2ImgRequest, context) -> pb2.Img2ImgResponse:
        """Handle single image generation request."""
        request_id = self.request_counter
        self.request_counter += 1
        self.logger.info(f"Received Img2Img request {request_id}")
        
        # Process the request
        try:
            start_time = time.time()
            generated_image = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.model.generate_image,
                request.image,
                request.prompt,
                request.num_inference_steps,
                request.strength,
                request.guidance_scale,
                request.seed
            )
            
            return pb2.Img2ImgResponse(
                generated_image=generated_image,
                request_id=request_id,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            self.logger.error(f"Error processing request {request_id}: {str(e)}")
            raise

    async def Img2ImgBatch(self, request: pb2.Img2ImgBatchRequest, context) -> pb2.Img2ImgBatchResponse:
        """Handle batch image generation request."""
        request_id = self.request_counter
        self.request_counter += 1
        self.logger.info(f"Received Img2ImgBatch request {request_id}")
        
        # Process the request
        try:
            start_time = time.time()
            generated_images = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.model.generate_batch,
                request.image,
                request.prompt,
                request.num_images,
                request.num_inference_steps,
                request.strength,
                request.guidance_scale,
                request.seed
            )
            
            return pb2.Img2ImgBatchResponse(
                generated_images=generated_images,
                request_id=request_id,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            self.logger.error(f"Error processing batch request {request_id}: {str(e)}")
            raise

    async def GetQueueStatus(self, request: pb2.QueueStatusRequest, context) -> pb2.QueueStatusResponse:
        status = self.request_queue.get_status()
        return pb2.QueueStatusResponse(
            queue_length=status["queue_length"],
            estimated_wait_time_ms=status["estimated_wait_time_ms"],
            active_requests=status["active_requests"]
        )

    def _process_single_request(self, request_id: str):
        request_data = asyncio.run(self.request_queue.get_request())
        return self.model.generate_image(
            image_bytes=request_data[1]["image_bytes"],
            prompt=request_data[1]["prompt"],
            num_inference_steps=request_data[1]["num_inference_steps"],
            strength=request_data[1]["strength"],
            guidance_scale=request_data[1]["guidance_scale"],
            seed=request_data[1]["seed"]
        )

    def _process_batch_request(self, request_id: str):
        request_data = asyncio.run(self.request_queue.get_request())
        return self.model.generate_batch(
            image_bytes=request_data[1]["image_bytes"],
            prompt=request_data[1]["prompt"],
            num_images=request_data[1]["num_images"],
            num_inference_steps=request_data[1]["num_inference_steps"],
            strength=request_data[1]["strength"],
            guidance_scale=request_data[1]["guidance_scale"],
            seed=request_data[1]["seed"]
        )

async def serve():
    logging.basicConfig(level=logging.INFO)
    server = aio.server()
    pb2_grpc.add_SDXLTurboServiceServicer_to_server(SDXLTurboServicer(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    logging.info("Server started on port 50051")
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve()) 