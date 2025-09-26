#!/usr/bin/env python3
"""
Main ETL Pipeline Runner
Python equivalent of EthBlockEventsApplication main method
"""
import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from config import get_config
from etl_python.services.ethereum_client import EthereumClient
from etl_python.services.event_listener import EventListenerService
from etl_python.services.event_handler import EventHandlerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


class ETLPipeline:
    """Main ETL Pipeline orchestrator"""
    
    def __init__(self):
        self.config = get_config()
        self.ethereum_client = None
        self.event_listener = None
        self.event_handler = None
        self.running = False
    
    async def initialize(self):
        """Initialize all ETL components"""
        logger.info("Initializing ETL Pipeline...")
        
        # Initialize Ethereum client
        self.ethereum_client = EthereumClient(
            node_url=self.config.ethereum.node_url,
            websocket_url=self.config.ethereum.websocket_url
        )
        
        # Initialize event handler (must be before event listener)
        self.event_handler = EventHandlerService()
        self.event_handler.initialize()
        
        # Initialize event listener with contracts
        self.event_listener = EventListenerService(
            ethereum_client=self.ethereum_client,
            contracts=self.config.ethereum.contracts
        )
        
        logger.info("ETL Pipeline initialized successfully")
    
    async def start(self):
        """Start the complete ETL pipeline"""
        logger.info("Starting ETL Pipeline...")
        self.running = True
        
        # Start all services concurrently
        tasks = []
        
        # Start block listening
        if self.ethereum_client.get_web3_websocket():
            tasks.append(asyncio.create_task(self.ethereum_client.start_block_listening()))
        
        # Start event listening
        tasks.append(asyncio.create_task(self.event_listener.start_listening()))
        
        logger.info("ETL Pipeline started successfully")
        
        # Wait for all tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop(self):
        """Stop the ETL pipeline gracefully"""
        logger.info("Stopping ETL Pipeline...")
        self.running = False
        
        if self.event_listener:
            self.event_listener.stop_listening()
        
        logger.info("ETL Pipeline stopped")
    
    async def run_forever(self):
        """Run the pipeline until interrupted"""
        await self.initialize()
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            await self.start()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
        finally:
            await self.stop()


async def main():
    """Main entry point"""
    logger.info("Starting ETH Block Events ETL Pipeline")
    
    try:
        pipeline = ETLPipeline()
        await pipeline.run_forever()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("ETL Pipeline completed")


if __name__ == "__main__":
    asyncio.run(main())