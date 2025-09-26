#!/usr/bin/env python3
"""
Setup script for ETH Block Events Python ETL
Initializes the environment and validates setup
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


def check_python_version():
    """Check if Python version meets requirements"""
    logger.info("Checking Python version...")
    
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"Python version: {sys.version}")
    return True


def install_dependencies():
    """Install Python dependencies"""
    logger.info("Installing Python dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        logger.error("requirements.txt not found")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, capture_output=True, text=True)
        
        logger.info("Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False


def create_env_file():
    """Create .env file from template if it doesn't exist"""
    logger.info("Checking for .env file...")
    
    env_file = Path(__file__).parent / ".env"
    sample_env_file = Path(__file__).parent / "application-local-sample.yml"
    
    if env_file.exists():
        logger.info(".env file already exists")
        return True
    
    logger.info("Creating .env file from template...")
    
    env_content = """# ETH Block Events Python ETL Environment Variables
# Copy this file to .env and update with your actual values

# Ethereum Node Configuration
ETHEREUM_NODE_URL=https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID
ETHEREUM_WS_URL=wss://mainnet.infura.io/ws/v3/YOUR_INFURA_PROJECT_ID

# Logging Configuration
LOG_LEVEL=INFO

# Optional: Database Configuration (if using database loader)
# DATABASE_URL=postgresql://user:password@localhost:5432/ethblockevents

# Optional: Webhook Configuration (if using webhook loader)
# WEBHOOK_URL=https://your-webhook-endpoint.com/events

# Development Settings
DEBUG=false
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info(f".env file created at {env_file}")
        logger.warning("⚠️  Please update the .env file with your actual Infura project ID")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create .env file: {e}")
        return False


def validate_configuration():
    """Validate the configuration setup"""
    logger.info("Validating configuration...")
    
    try:
        # Add current directory to Python path for imports
        sys.path.insert(0, str(Path(__file__).parent))
        
        from config import get_config
        
        config = get_config()
        
        # Check if Infura URLs are properly configured
        if "YOUR_INFURA_PROJECT_ID" in config.ethereum.node_url:
            logger.warning("⚠️  Infura project ID not configured in YAML files")
            logger.info("Please update your application-local.yml or .env file with actual Infura credentials")
        else:
            logger.info("✅ Ethereum node URL configured")
        
        if "YOUR_INFURA_PROJECT_ID" in config.ethereum.websocket_url:
            logger.warning("⚠️  Infura WebSocket URL not configured")
        else:
            logger.info("✅ Ethereum WebSocket URL configured")
        
        logger.info(f"✅ Configuration loaded with {len(config.ethereum.contracts)} contracts")
        return True
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def test_ethereum_connection():
    """Test connection to Ethereum node"""
    logger.info("Testing Ethereum connection...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        
        from etl_python.services.ethereum_client import EthereumClient
        from config import get_config
        
        config = get_config()
        
        # Skip test if using default URLs
        if "YOUR_INFURA_PROJECT_ID" in config.ethereum.node_url:
            logger.warning("Skipping Ethereum connection test - Infura not configured")
            return True
        
        client = EthereumClient(
            node_url=config.ethereum.node_url,
            websocket_url=config.ethereum.websocket_url
        )
        
        latest_block = client.get_latest_block_number()
        logger.info(f"✅ Ethereum connection successful - Latest block: {latest_block}")
        return True
        
    except Exception as e:
        logger.error(f"Ethereum connection test failed: {e}")
        logger.info("This is expected if you haven't configured your Infura credentials yet")
        return False


def create_sample_data():
    """Create sample data for testing"""
    logger.info("Creating sample data files...")
    
    sample_dir = Path(__file__).parent / "sample_data"
    sample_dir.mkdir(exist_ok=True)
    
    # Create sample extracted data
    sample_extracted = {
        "extraction_timestamp": "2024-01-01T12:00:00",
        "block_range": {
            "from_block": 19000000,
            "to_block": 19000010,
            "block_count": 10
        },
        "latest_block": {
            "block_number": 19000010,
            "block_event": {
                "block_number": 19000010,
                "block_hash": "0x1234567890abcdef",
                "timestamp": "2024-01-01T12:00:00",
                "transaction_count": 150,
                "gas_used": 15000000,
                "gas_limit": 30000000
            }
        },
        "events": {
            "USDC": [
                {
                    "transactionHash": "0xabcdef1234567890",
                    "blockNumber": 19000005,
                    "topics": [
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                        "0x000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                        "0x000000000000000000000000742daa7c73f8c8b32f93e8cfa14c45f4b82ed5f8"
                    ],
                    "data": "0x0000000000000000000000000000000000000000000000000000000002faf080",
                    "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
                }
            ]
        },
        "summary": {
            "total_events": 1,
            "contracts_monitored": 1,
            "active_events": 1
        }
    }
    
    import json
    
    with open(sample_dir / "sample_extracted_data.json", 'w') as f:
        json.dump(sample_extracted, f, indent=2)
    
    logger.info(f"✅ Sample data created in {sample_dir}")
    return True


def print_next_steps():
    """Print next steps for the user"""
    logger.info("\n" + "="*60)
    logger.info("SETUP COMPLETED SUCCESSFULLY!")
    logger.info("="*60)
    
    print("\n📋 NEXT STEPS:")
    print("\n1. Configure your Infura credentials:")
    print("   - Copy application-local-sample.yml to application-local.yml")
    print("   - Replace YOUR_INFURA_PROJECT_ID with your actual Infura project ID")
    print("   - Or update the .env file with your credentials")
    
    print("\n2. Test the setup:")
    print("   python extract_data.py --recent 5")
    
    print("\n3. Run the complete ETL pipeline:")
    print("   python main_etl.py")
    
    print("\n4. Run individual ETL phases:")
    print("   python extract_data.py --output extracted.json")
    print("   python transform_data.py extracted.json --output transformed.json")
    print("   python load_data.py transformed.json --output console")
    
    print("\n5. Try with sample data:")
    print("   python transform_data.py sample_data/sample_extracted_data.json")
    print("   python load_data.py sample_data/sample_extracted_data.json")
    
    print("\n📚 For more information, see the updated README.md")
    print("="*60)


def main():
    """Main setup function"""
    logger.info("Starting ETH Block Events Python ETL Setup...")
    
    success = True
    
    # Run setup steps
    success &= check_python_version()
    success &= install_dependencies()
    success &= create_env_file()
    success &= validate_configuration()
    success &= create_sample_data()
    
    # Optional tests (don't fail setup if they don't work)
    test_ethereum_connection()
    
    if success:
        print_next_steps()
        logger.info("Setup completed successfully!")
        return 0
    else:
        logger.error("Setup failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())