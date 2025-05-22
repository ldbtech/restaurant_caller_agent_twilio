import os
import sys
import logging
from pathlib import Path

# Add both the project root and app directory to Python path
project_root = Path(__file__).parent
app_dir = project_root / "app"
proto_dir = app_dir / "proto"
sys.path.extend([str(project_root), str(app_dir), str(proto_dir)])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        # Import after setting up the path
        from app.grpc_server import serve
        logger.info("Starting Auth Service...")
        serve()
    except KeyboardInterrupt:
        logger.info("Shutting down Auth Service...")
    except Exception as e:
        logger.error(f"Error starting Auth Service: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
