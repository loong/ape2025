"""Configuration settings and constants for the application."""

# File paths
TEST_IMAGE_PATH = "../../seed-images/hanbok-red.jpg"

# Server settings
GRPC_SERVER_ADDRESS = "localhost:50051"

# Default values
DEFAULT_PROMPT = "trade"
DEFAULT_FPS = 1.0
DEFAULT_NUM_IMAGES = 10
DEFAULT_NUM_GENERATED_IMAGES = 5

# Timing constants
CONNECTION_LOG_INTERVAL = 60  # seconds
IMAGE_SEND_INTERVAL = 1.0  # seconds

# Canvas settings
CANVAS_SLUGS = ["left-canva", "right-canva"]

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s"
} 