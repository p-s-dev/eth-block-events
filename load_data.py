#!/usr/bin/env python3
"""
Data Loading Phase
Load transformed data into storage systems, databases, or external APIs
"""
import asyncio
import logging
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from config import get_config

# Only import aiohttp when needed
aiohttp = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


class DataLoader:
    """Data loading service for transformed Ethereum data"""
    
    def __init__(self):
        self.config = get_config()
        self.load_statistics = {
            'events_loaded': 0,
            'blocks_loaded': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    async def load_to_console(self, transformed_data: Dict[str, Any]):
        """Load data to console output (simplest loader)"""
        logger.info("Loading data to console...")
        self.load_statistics['start_time'] = datetime.now()
        
        print("\n" + "="*80)
        print("ETHEREUM BLOCKCHAIN DATA ANALYSIS REPORT")
        print("="*80)
        
        # Load metadata
        metadata = transformed_data.get('metadata', {})
        print(f"\nExtraction Time: {metadata.get('original_extraction_timestamp', 'Unknown')}")
        print(f"Transformation Time: {metadata.get('transformation_timestamp', 'Unknown')}")
        print(f"Block Range: {metadata.get('block_range', {})}")
        
        # Load block data
        block_data = transformed_data.get('transformed_blocks', {})
        if block_data:
            await self._load_block_data_to_console(block_data)
            self.load_statistics['blocks_loaded'] += 1
        
        # Load events data
        events_data = transformed_data.get('transformed_events', {})
        for contract_name, contract_data in events_data.items():
            await self._load_contract_events_to_console(contract_name, contract_data)
        
        # Load analytics
        analytics = transformed_data.get('analytics', {})
        if analytics:
            await self._load_analytics_to_console(analytics)
        
        self.load_statistics['end_time'] = datetime.now()
        print(f"\nData loading completed. Statistics: {self.load_statistics}")
        print("="*80)
    
    async def load_to_file(self, transformed_data: Dict[str, Any], output_format: str = "json"):
        """Load data to file storage"""
        logger.info(f"Loading data to file storage in {output_format} format...")
        self.load_statistics['start_time'] = datetime.now()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format.lower() == "json":
            await self._load_to_json_file(transformed_data, f"loaded_data_{timestamp}.json")
        elif output_format.lower() == "csv":
            await self._load_to_csv_files(transformed_data, timestamp)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        self.load_statistics['end_time'] = datetime.now()
        logger.info(f"Data loading completed. Statistics: {self.load_statistics}")
    
    async def load_to_webhook(self, transformed_data: Dict[str, Any], webhook_url: str):
        """Load data to external webhook/API"""
        logger.info(f"Loading data to webhook: {webhook_url}")
        self.load_statistics['start_time'] = datetime.now()
        
        try:
            # Import aiohttp only when needed
            global aiohttp
            if aiohttp is None:
                try:
                    import aiohttp
                except ImportError:
                    logger.error("aiohttp is required for webhook loading. Install with: pip install aiohttp")
                    self.load_statistics['errors'] += 1
                    return
            
            # Split data into chunks for large datasets
            chunks = self._chunk_data_for_api(transformed_data)
            
            async with aiohttp.ClientSession() as session:
                for i, chunk in enumerate(chunks):
                    try:
                        async with session.post(
                            webhook_url,
                            json=chunk,
                            headers={'Content-Type': 'application/json'}
                        ) as response:
                            
                            if response.status == 200:
                                logger.info(f"Successfully sent chunk {i+1}/{len(chunks)}")
                                self.load_statistics['events_loaded'] += chunk.get('event_count', 0)
                            else:
                                logger.error(f"Failed to send chunk {i+1}: HTTP {response.status}")
                                self.load_statistics['errors'] += 1
                                
                    except Exception as e:
                        logger.error(f"Error sending chunk {i+1}: {e}")
                        self.load_statistics['errors'] += 1
        
        except Exception as e:
            logger.error(f"Failed to load data to webhook: {e}")
            self.load_statistics['errors'] += 1
        
        self.load_statistics['end_time'] = datetime.now()
    
    async def load_to_database(self, transformed_data: Dict[str, Any], connection_string: str = None):
        """Load data to database (placeholder - would need actual DB implementation)"""
        logger.info("Loading data to database...")
        self.load_statistics['start_time'] = datetime.now()
        
        # This is a placeholder implementation
        # In a real scenario, you would:
        # 1. Connect to your database (PostgreSQL, MySQL, MongoDB, etc.)
        # 2. Create/validate table schemas  
        # 3. Insert data in batches
        # 4. Handle conflicts/updates
        
        logger.warning("Database loading is not implemented - this is a placeholder")
        logger.info("To implement database loading:")
        logger.info("1. Install database driver (psycopg2, pymongo, etc.)")
        logger.info("2. Implement connection and schema management")
        logger.info("3. Add batch insertion logic")
        logger.info("4. Handle data conflicts and updates")
        
        # Simulate loading process
        await asyncio.sleep(1)
        
        # Count what would be loaded
        events_count = 0
        for contract_data in transformed_data.get('transformed_events', {}).values():
            if isinstance(contract_data, dict):
                if 'events' in contract_data:
                    events_count += len(contract_data['events'])
                elif 'swap_events' in contract_data:
                    events_count += (len(contract_data.get('swap_events', [])) +
                                   len(contract_data.get('initialize_events', [])) +
                                   len(contract_data.get('liquidity_events', [])))
        
        self.load_statistics['events_loaded'] = events_count
        self.load_statistics['blocks_loaded'] = 1 if transformed_data.get('transformed_blocks') else 0
        self.load_statistics['end_time'] = datetime.now()
        
        logger.info(f"Database loading simulation completed. Would load {events_count} events")
    
    async def _load_block_data_to_console(self, block_data: Dict[str, Any]):
        """Load block data to console"""
        transformed_block = block_data.get('transformed_block', {})
        
        print(f"\n--- LATEST BLOCK ANALYSIS ---")
        print(f"Block Number: {transformed_block.get('block_number')}")
        print(f"Block Hash: {transformed_block.get('block_hash', '')[:20]}...")
        print(f"Timestamp: {transformed_block.get('timestamp')}")
        print(f"Transactions: {transformed_block.get('transaction_count')}")
        print(f"Gas Used: {transformed_block.get('gas_used'):,} / {transformed_block.get('gas_limit'):,}")
        print(f"Gas Utilization: {transformed_block.get('gas_utilization_percent')}%")
        
        network_health = transformed_block.get('network_health', {})
        print(f"Network Status: {network_health.get('utilization_status', 'unknown').upper()}")
        if network_health.get('is_full_block'):
            print("⚠️  WARNING: Block is nearly full!")
    
    async def _load_contract_events_to_console(self, contract_name: str, contract_data: Dict[str, Any]):
        """Load contract events to console"""
        print(f"\n--- {contract_name.upper()} CONTRACT EVENTS ---")
        
        if 'events' in contract_data:
            # ERC20 or generic events
            events = contract_data['events']
            summary = contract_data.get('summary', {})
            
            print(f"Total Events: {len(events)}")
            
            if 'total_transfers' in summary:
                # ERC20 specific
                print(f"Total Transfers: {summary['total_transfers']}")
                print(f"Total Volume: {summary.get('total_volume', 0)}")
                print(f"Unique Addresses: {summary.get('unique_addresses', 0)}")
                
                # Show top transfers
                top_transfers = summary.get('top_transfers', [])[:3]
                if top_transfers:
                    print("Top Transfers:")
                    for i, transfer in enumerate(top_transfers, 1):
                        print(f"  {i}. {transfer.get('value_decimal', 0)} tokens "
                              f"({transfer.get('from_address', '')[:8]}... → "
                              f"{transfer.get('to_address', '')[:8]}...)")
            
        elif 'swap_events' in contract_data:
            # Uniswap events
            summary = contract_data.get('summary', {})
            print(f"Swap Events: {summary.get('total_swaps', 0)}")
            print(f"Pool Initializations: {summary.get('total_initializations', 0)}")
            print(f"Liquidity Changes: {summary.get('total_liquidity_changes', 0)}")
            print(f"Unique Pools: {summary.get('unique_pools', 0)}")
        
        self.load_statistics['events_loaded'] += contract_data.get('event_count', 0)
    
    async def _load_analytics_to_console(self, analytics: Dict[str, Any]):
        """Load analytics to console"""
        print(f"\n--- CROSS-CONTRACT ANALYTICS ---")
        print(f"Total Events Processed: {analytics.get('total_events_processed', 0)}")
        print(f"Contracts Analyzed: {analytics.get('contracts_analyzed', 0)}")
        
        event_distribution = analytics.get('event_distribution', {})
        if event_distribution:
            print("Event Distribution by Contract:")
            for contract, count in event_distribution.items():
                percentage = (count / analytics.get('total_events_processed', 1)) * 100
                print(f"  {contract}: {count} events ({percentage:.1f}%)")
    
    async def _load_to_json_file(self, data: Dict[str, Any], filename: str):
        """Load data to JSON file"""
        logger.info(f"Saving data to {filename}")
        
        def json_encoder(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return str(obj)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=json_encoder)
        
        logger.info(f"Data saved to {filename}")
    
    async def _load_to_csv_files(self, data: Dict[str, Any], timestamp: str):
        """Load data to CSV files"""
        logger.info("Saving data to CSV files")
        
        # This would require pandas or csv module
        logger.warning("CSV export not fully implemented - would need pandas")
        logger.info("To implement CSV export:")
        logger.info("1. pip install pandas")
        logger.info("2. Convert nested JSON to flat DataFrames")
        logger.info("3. Export each data type to separate CSV files")
        
        # Create a simple summary CSV as placeholder
        summary_file = f"data_summary_{timestamp}.csv"
        with open(summary_file, 'w') as f:
            f.write("metric,value\n")
            f.write(f"transformation_timestamp,{data.get('metadata', {}).get('transformation_timestamp', '')}\n")
            f.write(f"contracts_analyzed,{data.get('analytics', {}).get('contracts_analyzed', 0)}\n")
            f.write(f"total_events,{data.get('analytics', {}).get('total_events_processed', 0)}\n")
        
        logger.info(f"Summary saved to {summary_file}")
    
    def _chunk_data_for_api(self, data: Dict[str, Any], max_chunk_size: int = 1000) -> List[Dict[str, Any]]:
        """Split large datasets into smaller chunks for API transmission"""
        chunks = []
        
        # Create base chunk with metadata
        base_chunk = {
            'metadata': data.get('metadata', {}),
            'analytics': data.get('analytics', {}),
            'chunk_info': {}
        }
        
        # Handle events data
        events_data = data.get('transformed_events', {})
        
        for contract_name, contract_data in events_data.items():
            if isinstance(contract_data, dict) and 'events' in contract_data:
                events = contract_data['events']
                
                # Split events into chunks
                for i in range(0, len(events), max_chunk_size):
                    chunk = base_chunk.copy()
                    chunk['contract_name'] = contract_name
                    chunk['events'] = events[i:i + max_chunk_size]
                    chunk['event_count'] = len(chunk['events'])
                    chunk['chunk_info'] = {
                        'chunk_index': len(chunks),
                        'start_index': i,
                        'end_index': min(i + max_chunk_size, len(events)),
                        'total_events': len(events)
                    }
                    chunks.append(chunk)
        
        # If no events, create single chunk with other data
        if not chunks:
            chunks.append({
                **base_chunk,
                'transformed_blocks': data.get('transformed_blocks', {}),
                'event_count': 0
            })
        
        return chunks


async def main():
    """Main entry point for data loading"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load transformed Ethereum blockchain data")
    parser.add_argument("input_file", help="Input JSON file with transformed data")
    parser.add_argument("--output", choices=["console", "file", "webhook", "database"], 
                       default="console", help="Output destination")
    parser.add_argument("--format", choices=["json", "csv"], default="json", 
                       help="Output format (for file output)")
    parser.add_argument("--webhook-url", type=str, help="Webhook URL (for webhook output)")
    parser.add_argument("--db-connection", type=str, help="Database connection string")
    
    args = parser.parse_args()
    
    try:
        # Load input data
        logger.info(f"Loading transformed data from {args.input_file}")
        with open(args.input_file, 'r') as f:
            transformed_data = json.load(f)
        
        loader = DataLoader()
        
        if args.output == "console":
            await loader.load_to_console(transformed_data)
        elif args.output == "file":
            await loader.load_to_file(transformed_data, args.format)
        elif args.output == "webhook":
            if not args.webhook_url:
                logger.error("Webhook URL is required for webhook output")
                sys.exit(1)
            await loader.load_to_webhook(transformed_data, args.webhook_url)
        elif args.output == "database":
            await loader.load_to_database(transformed_data, args.db_connection)
        
        logger.info("Data loading completed successfully")
        
    except Exception as e:
        logger.error(f"Data loading failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())