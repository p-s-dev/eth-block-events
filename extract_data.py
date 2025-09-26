#!/usr/bin/env python3
"""
Data Extraction Phase
Extract Ethereum events and block data from the blockchain
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
import json

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from config import get_config
from etl_python.services.ethereum_client import EthereumClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


class DataExtractor:
    """Data extraction service for Ethereum blockchain data"""
    
    def __init__(self):
        self.config = get_config()
        self.ethereum_client = None
    
    def initialize(self):
        """Initialize the data extractor"""
        logger.info("Initializing Data Extractor...")
        
        self.ethereum_client = EthereumClient(
            node_url=self.config.ethereum.node_url,
            websocket_url=self.config.ethereum.websocket_url
        )
        
        logger.info("Data Extractor initialized")
    
    def extract_block_data(self, block_number: int = None) -> Dict[str, Any]:
        """Extract data from a specific block"""
        if block_number is None:
            block_number = self.ethereum_client.get_latest_block_number()
        
        logger.info(f"Extracting block data for block {block_number}")
        
        block_data = self.ethereum_client.get_block(block_number)
        block_event = self.ethereum_client.create_block_event(block_data)
        
        return {
            'block_number': block_number,
            'block_event': block_event.dict(),
            'raw_block_data': dict(block_data)
        }
    
    def extract_contract_events(self, contract_address: str, from_block: int = None, 
                              to_block: int = None, event_signatures: List[str] = None) -> List[Dict[str, Any]]:
        """Extract events from a specific contract"""
        logger.info(f"Extracting events from contract {contract_address}")
        
        topics = event_signatures if event_signatures else None
        logs = self.ethereum_client.get_contract_logs(
            contract_address=contract_address,
            from_block=from_block,
            to_block=to_block,
            topics=topics
        )
        
        logger.info(f"Extracted {len(logs)} events from {contract_address}")
        return logs
    
    def extract_all_configured_events(self, from_block: int = None, to_block: int = None) -> Dict[str, Any]:
        """Extract events from all configured contracts"""
        logger.info("Extracting events from all configured contracts")
        
        all_events = {}
        
        for contract in self.config.ethereum.contracts:
            contract_events = []
            
            for event_config in contract.events:
                if event_config.enabled:
                    events = self.extract_contract_events(
                        contract_address=contract.address,
                        from_block=from_block,
                        to_block=to_block,
                        event_signatures=[event_config.signature]
                    )
                    
                    # Add metadata to each event
                    for event in events:
                        event['contract_name'] = contract.name
                        event['event_name'] = event_config.name
                        event['event_signature'] = event_config.signature
                    
                    contract_events.extend(events)
            
            all_events[contract.name] = contract_events
        
        return all_events
    
    def extract_recent_data(self, block_count: int = 100) -> Dict[str, Any]:
        """Extract recent blockchain data (last N blocks)"""
        logger.info(f"Extracting recent data for last {block_count} blocks")
        
        latest_block = self.ethereum_client.get_latest_block_number()
        from_block = max(0, latest_block - block_count)
        
        # Extract block information
        block_data = self.extract_block_data(latest_block)
        
        # Extract events
        events_data = self.extract_all_configured_events(
            from_block=from_block,
            to_block=latest_block
        )
        
        return {
            'extraction_timestamp': block_data['block_event']['timestamp'],
            'block_range': {
                'from_block': from_block,
                'to_block': latest_block,
                'block_count': block_count
            },
            'latest_block': block_data,
            'events': events_data,
            'summary': {
                'total_events': sum(len(events) for events in events_data.values()),
                'contracts_monitored': len(self.config.ethereum.contracts),
                'active_events': sum(1 for contract in self.config.ethereum.contracts 
                                   for event in contract.events if event.enabled)
            }
        }
    
    def save_extracted_data(self, data: Dict[str, Any], output_file: str = None):
        """Save extracted data to file"""
        if output_file is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"extracted_data_{timestamp}.json"
        
        logger.info(f"Saving extracted data to {output_file}")
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Data saved to {output_file}")


async def main():
    """Main entry point for data extraction"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract Ethereum blockchain data")
    parser.add_argument("--block", type=int, help="Specific block number to extract")
    parser.add_argument("--contract", type=str, help="Specific contract address to extract events from")
    parser.add_argument("--from-block", type=int, help="Start block for range extraction")
    parser.add_argument("--to-block", type=int, help="End block for range extraction") 
    parser.add_argument("--recent", type=int, default=100, help="Extract recent N blocks (default: 100)")
    parser.add_argument("--output", type=str, help="Output file path")
    
    args = parser.parse_args()
    
    try:
        extractor = DataExtractor()
        extractor.initialize()
        
        if args.block:
            # Extract specific block
            data = extractor.extract_block_data(args.block)
        elif args.contract:
            # Extract events from specific contract
            events = extractor.extract_contract_events(
                contract_address=args.contract,
                from_block=args.from_block,
                to_block=args.to_block
            )
            data = {
                'contract_address': args.contract,
                'events': events,
                'event_count': len(events)
            }
        else:
            # Extract recent data
            data = extractor.extract_recent_data(args.recent)
        
        # Save data
        extractor.save_extracted_data(data, args.output)
        
        logger.info("Data extraction completed successfully")
        
    except Exception as e:
        logger.error(f"Data extraction failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())