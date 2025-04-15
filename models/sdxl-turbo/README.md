# SDXL-Turbo gRPC Server

A high-performance Python server that serves the SDXL-Turbo model for image-to-image generation using gRPC. The server implements a queue system for handling multiple concurrent requests and operates on localhost.

## Features

- Image-to-image generation using SDXL-Turbo
- Support for both single image and batch generation
- Efficient queue management system
- MPS (Metal Performance Shaders) acceleration support
- Comprehensive error handling and monitoring

## Requirements

- Python 3.10+
- MacBook Pro with M4 chip (or compatible Apple Silicon)
- Xcode Command Line Tools

## Installation

1. Clone the repository and navigate to the server directory:
```bash
cd models/sdxl-turbo
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Generate gRPC protocol files:
```bash
chmod +x generate_proto.sh
./generate_proto.sh
```

## Usage

### Starting the Server

Run the server:
```bash
python server.py
```

The server will start on `localhost:50051` by default.

### Using the Client

The client supports three modes of operation:

1. Single Image Generation:
```bash
python client.py --mode single --image path/to/input/image.jpg --prompt "your prompt here" --output output.png
```

2. Batch Image Generation:
```bash
python client.py --mode batch --image path/to/input/image.jpg --prompt "your prompt here" --num-images 4 --output-prefix output_batch
```

3. Check Queue Status:
```bash
python client.py --mode status
```

### Client Arguments

- `--mode`: Choose between 'single', 'batch', or 'status'
- `--image`: Path to input image (required for single and batch modes)
- `--prompt`: Text prompt for generation (required for single and batch modes)
- `--output`: Output file path (for single mode)
- `--output-prefix`: Prefix for output files (for batch mode)
- `--num-images`: Number of images to generate (for batch mode)

## API Endpoints

1. **Img2Img**
   - Input: Image data, prompt, and generation parameters
   - Output: Generated image
   - Purpose: Generate a single image based on input image and prompt

2. **Img2ImgBatch**
   - Input: Image data, prompt, number of images, and generation parameters
   - Output: Array of generated images
   - Purpose: Generate multiple variations of an image

3. **GetQueueStatus**
   - Input: None
   - Output: Current queue status and metrics
   - Purpose: Monitor server performance and queue status

## Generation Parameters

- `num_inference_steps` (int, default=2): Number of inference steps
- `strength` (float, default=0.8): Strength parameter for generation
- `guidance_scale` (float, default=0.0): Guidance scale for generation
- `seed` (int, default=0): Random seed for reproducibility

## Error Handling

The server implements comprehensive error handling for:
- Input validation errors
- Processing errors
- System errors

All errors are logged with appropriate status codes and error messages.

## Performance Optimization

- Model loaded once at server startup
- MPS acceleration for Apple Silicon
- Efficient memory management
- Single worker thread for MPS compatibility
- In-memory image processing

## Monitoring

The server provides:
- Request count and timing statistics
- Queue length and wait times
- Memory and MPS usage metrics
- Error rate tracking

## Troubleshooting

1. If you encounter gRPC installation issues:
```bash
pip install grpcio==1.60.0 --no-binary :all:
pip install grpcio-tools==1.60.0 --no-binary :all:
```

2. If you get module import errors:
```bash
PYTHONPATH=$PYTHONPATH:. python server.py
```

3. For MPS-related issues:
- Ensure you're using a compatible Apple Silicon Mac
- Check that PyTorch is properly installed with MPS support
- Verify that the model is loaded on the correct device

## Future Improvements

- Containerization with Docker
- Support for additional models
- Text-to-image generation
- Extended parameter sets
- Enhanced monitoring and metrics
