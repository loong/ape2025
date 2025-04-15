# Interactive Art Image Streaming Application

A high-performance image streaming and generation application that displays interactive art on multiple web canvases. The application supports both pre-generated image streaming and real-time image generation using SDXL-Turbo.

## Features

- Real-time image streaming to multiple web canvases
- Fast image-to-image generation using SDXL-Turbo
- Support for both single and batch image generation
- Efficient WebSocket connection management
- Comprehensive error handling and monitoring
- Optimized for MPS acceleration on Apple Silicon

## Requirements

- Python 3.10+
- Apple Silicon Mac (M1/M2/M3/M4)
- macOS 12.0 or later
- Node.js 16+ (for frontend development)

## Project Structure

```
psyche/
├── backend/
│   ├── main.py              # Main application entry point
│   ├── config.py            # Configuration settings
│   ├── websocket_manager.py # WebSocket connection handling
│   ├── image_handler.py     # Image processing and sending
│   ├── inference_client.py  # SDXL-Turbo service interaction
│   └── requirements.txt     # Backend dependencies
├── models/
│   └── sdxl-turbo/          # SDXL-Turbo service
└── frontend/                # React frontend application
```

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. Install backend dependencies:
```bash
cd psyche/backend
pip install -r requirements.txt
```

3. Generate gRPC Python files for SDXL-Turbo:
```bash
cd ../models/sdxl-turbo
chmod +x generate_proto.sh
./generate_proto.sh
```

4. Install frontend dependencies:
```bash
cd ../../frontend
npm install
```

## Usage

### Starting the SDXL-Turbo Service

Run the SDXL-Turbo service:
```bash
cd models/sdxl-turbo
python server.py
```

The service will start on `localhost:50051`.

### Starting the Main Application

Run the main application:
```bash
cd psyche/backend
python main.py
```

The application will start on `localhost:8000`.

### Starting the Frontend

Run the frontend development server:
```bash
cd psyche/frontend
npm start
```

The frontend will start on `localhost:3000`.

## API Endpoints

### WebSocket
- `/ws/{canvas_slug}`: WebSocket endpoint for canvas connections
- Purpose: Real-time image streaming to specific canvases

### HTTP
- `/test-stream/{canvas_slug}/{num_images}/{fps}`: Test endpoint for streaming test images
- `/test-inference`: Test endpoint for generating images using SDXL-Turbo

## Performance Considerations

- The application uses a modular structure for better maintainability
- WebSocket connections are managed efficiently per canvas
- Image processing is optimized for real-time streaming
- SDXL-Turbo service uses MPS acceleration for fast image generation
- Proper resource cleanup is implemented in all modules

## Error Handling

The application provides comprehensive error handling for:
- WebSocket connection issues
- Image processing errors
- SDXL-Turbo service communication
- Invalid input parameters
- System resource issues

## Monitoring

The application logs:
- WebSocket connection status
- Image streaming performance
- SDXL-Turbo service interactions
- Error conditions
- System resource usage

## License

MIT License 