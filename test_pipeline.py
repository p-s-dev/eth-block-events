#!/usr/bin/env python3
"""
Test script to validate the complete Python ETL pipeline
Demonstrates end-to-end functionality with sample data
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


async def test_pipeline():
    """Test the complete ETL pipeline with sample data"""
    logger.info("🧪 Starting ETL Pipeline Test")
    
    # Test 1: Configuration loading
    logger.info("1️⃣ Testing configuration loading...")
    try:
        from config import get_config
        config = get_config()
        logger.info(f"✅ Configuration loaded: {len(config.ethereum.contracts)} contracts configured")
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False
    
    # Test 2: Event models
    logger.info("2️⃣ Testing event models...")
    try:
        from etl_python.models.events import ERC20TransferEvent, UniswapSwapEvent, BlockEvent
        from datetime import datetime
        from decimal import Decimal
        
        # Test ERC20 event creation
        transfer_event = ERC20TransferEvent(
            contract_address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            block_number=19000000,
            transaction_hash="0x1234567890abcdef",
            log_index=0,
            timestamp=datetime.now(),
            from_address="0x1234567890123456789012345678901234567890",
            to_address="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            value=Decimal("1000000")
        )
        
        logger.info(f"✅ Event models working: {transfer_event.event_name} event created")
    except Exception as e:
        logger.error(f"❌ Event models test failed: {e}")
        return False
    
    # Test 3: Event bus
    logger.info("3️⃣ Testing event bus...")
    try:
        from etl_python.services.event_bus import EventBus, subscribe
        
        class TestHandler:
            def __init__(self):
                self.received_events = []
            
            @subscribe(ERC20TransferEvent)
            def handle_transfer(self, event):
                self.received_events.append(event)
        
        event_bus = EventBus("TestBus")
        handler = TestHandler()
        event_bus.register(handler)
        event_bus.post(transfer_event)
        
        if len(handler.received_events) == 1:
            logger.info("✅ Event bus working: Event delivered successfully")
        else:
            logger.error("❌ Event bus test failed: Event not delivered")
            return False
            
    except Exception as e:
        logger.error(f"❌ Event bus test failed: {e}")
        return False
    
    # Test 4: Data transformation
    logger.info("4️⃣ Testing data transformation...")
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "transform_data.py", 
            "sample_data/sample_extracted_data.json",
            "--output", "/tmp/test_transformed.json"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            logger.info("✅ Data transformation working: Sample data transformed successfully")
        else:
            logger.error(f"❌ Data transformation failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Data transformation test failed: {e}")
        return False
    
    # Test 5: Data loading
    logger.info("5️⃣ Testing data loading...")
    try:
        result = subprocess.run([
            sys.executable, "load_data.py", 
            "/tmp/test_transformed.json",
            "--output", "console"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0 and "ETHEREUM BLOCKCHAIN DATA ANALYSIS REPORT" in result.stdout:
            logger.info("✅ Data loading working: Console output generated successfully")
        else:
            logger.error(f"❌ Data loading failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Data loading test failed: {e}")
        return False
    
    # Test 6: File operations
    logger.info("6️⃣ Testing file operations...")
    try:
        import json
        
        # Check if transformed file was created
        transformed_file = Path("/tmp/test_transformed.json")
        if transformed_file.exists():
            with open(transformed_file) as f:
                data = json.load(f)
                
            if 'metadata' in data and 'transformed_events' in data:
                logger.info("✅ File operations working: Transformed data file created correctly")
            else:
                logger.error("❌ File operations failed: Transformed data structure invalid")
                return False
        else:
            logger.error("❌ File operations failed: Transformed data file not created")
            return False
            
    except Exception as e:
        logger.error(f"❌ File operations test failed: {e}")
        return False
    
    # All tests passed!
    logger.info("\n" + "="*60)
    logger.info("🎉 ALL TESTS PASSED! ETL Pipeline is working correctly!")
    logger.info("="*60)
    
    print("\n📊 TEST SUMMARY:")
    print("✅ Configuration loading - PASSED")
    print("✅ Event models - PASSED") 
    print("✅ Event bus - PASSED")
    print("✅ Data transformation - PASSED")
    print("✅ Data loading - PASSED")
    print("✅ File operations - PASSED")
    
    print("\n🚀 READY TO USE:")
    print("• Python ETL pipeline is fully functional")
    print("• All components tested and working")
    print("• Sample data processing confirmed")
    print("• Ready for production use with real Ethereum data")
    
    print("\n📝 NEXT STEPS:")
    print("1. Configure your Infura credentials in application-local.yml")
    print("2. Run: python main_etl.py (for real-time monitoring)")
    print("3. Or run individual phases with real blockchain data")
    
    return True


async def main():
    """Main test function"""
    success = await test_pipeline()
    
    if success:
        logger.info("🎯 ETL Pipeline test completed successfully!")
        return 0
    else:
        logger.error("💥 ETL Pipeline test failed!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))