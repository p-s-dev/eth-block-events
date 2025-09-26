#!/usr/bin/env python3
"""
Data Transformation Phase
Transform raw Ethereum event data into structured, analyzed formats
"""
import asyncio
import logging
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from config import get_config
from etl_python.models.events import EventSignatures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


class DataTransformer:
    """Data transformation service for Ethereum blockchain data"""
    
    def __init__(self):
        self.config = get_config()
    
    def transform_erc20_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform ERC20 transfer events into analyzed format"""
        logger.info(f"Transforming {len(events)} ERC20 events")
        
        transformed_events = []
        transfer_summary = {
            'total_transfers': 0,
            'total_volume': Decimal('0'),
            'unique_addresses': set(),
            'top_transfers': [],
            'hourly_volume': defaultdict(Decimal),
            'address_activity': defaultdict(int)
        }
        
        for event in events:
            if not self._is_erc20_transfer(event):
                continue
            
            # Extract and decode transfer data
            transformed_event = self._transform_erc20_transfer(event)
            transformed_events.append(transformed_event)
            
            # Update summary statistics
            transfer_summary['total_transfers'] += 1
            transfer_summary['total_volume'] += transformed_event['value_decimal']
            transfer_summary['unique_addresses'].add(transformed_event['from_address'])
            transfer_summary['unique_addresses'].add(transformed_event['to_address'])
            
            # Track hourly volume
            hour_key = transformed_event['timestamp'][:13]  # YYYY-MM-DDTHH
            transfer_summary['hourly_volume'][hour_key] += transformed_event['value_decimal']
            
            # Track address activity
            transfer_summary['address_activity'][transformed_event['from_address']] += 1
            transfer_summary['address_activity'][transformed_event['to_address']] += 1
        
        # Convert sets to counts and find top transfers
        transfer_summary['unique_addresses'] = len(transfer_summary['unique_addresses'])
        transfer_summary['top_transfers'] = sorted(
            transformed_events, 
            key=lambda x: x['value_decimal'], 
            reverse=True
        )[:10]
        
        # Convert defaultdicts to regular dicts for JSON serialization
        transfer_summary['hourly_volume'] = dict(transfer_summary['hourly_volume'])
        transfer_summary['address_activity'] = dict(transfer_summary['address_activity'])
        
        return {
            'events': transformed_events,
            'summary': transfer_summary,
            'transformation_timestamp': datetime.now().isoformat()
        }
    
    def transform_uniswap_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform Uniswap events into analyzed format"""
        logger.info(f"Transforming {len(events)} Uniswap events")
        
        swap_events = []
        initialize_events = []
        liquidity_events = []
        
        for event in events:
            event_signature = event.get('topics', [{}])[0] if event.get('topics') else None
            
            if event_signature == EventSignatures.UNISWAP_SWAP:
                swap_events.append(self._transform_uniswap_swap(event))
            elif event_signature == EventSignatures.UNISWAP_INITIALIZE:
                initialize_events.append(self._transform_uniswap_initialize(event))
            elif event_signature == EventSignatures.UNISWAP_MODIFY_LIQUIDITY:
                liquidity_events.append(self._transform_uniswap_liquidity(event))
        
        # Generate summary statistics
        summary = {
            'total_swaps': len(swap_events),
            'total_initializations': len(initialize_events),
            'total_liquidity_changes': len(liquidity_events),
            'unique_pools': len(set(e.get('pool_id', '') for e in swap_events + initialize_events + liquidity_events)),
            'trading_volume_events': len(swap_events),
            'new_pools_created': len(initialize_events)
        }
        
        return {
            'swap_events': swap_events,
            'initialize_events': initialize_events,
            'liquidity_events': liquidity_events,
            'summary': summary,
            'transformation_timestamp': datetime.now().isoformat()
        }
    
    def transform_block_data(self, block_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform block data into analyzed format"""
        logger.info("Transforming block data")
        
        raw_block = block_data.get('raw_block_data', {})
        block_event = block_data.get('block_event', {})
        
        # Calculate network statistics
        gas_utilization = (raw_block.get('gasUsed', 0) / raw_block.get('gasLimit', 1)) * 100
        
        transformed_block = {
            'block_number': raw_block.get('number'),
            'block_hash': raw_block.get('hash'),
            'timestamp': block_event.get('timestamp'),
            'transaction_count': len(raw_block.get('transactions', [])),
            'gas_used': raw_block.get('gasUsed'),
            'gas_limit': raw_block.get('gasLimit'),
            'gas_utilization_percent': round(gas_utilization, 2),
            'block_size': raw_block.get('size'),
            'difficulty': raw_block.get('difficulty'),
            'network_health': {
                'utilization_status': self._get_utilization_status(gas_utilization),
                'transaction_throughput': len(raw_block.get('transactions', [])),
                'is_full_block': gas_utilization > 95
            }
        }
        
        return {
            'transformed_block': transformed_block,
            'transformation_timestamp': datetime.now().isoformat()
        }
    
    def transform_extracted_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform complete extracted dataset"""
        logger.info("Transforming complete extracted dataset")
        
        transformed_data = {
            'metadata': {
                'original_extraction_timestamp': extracted_data.get('extraction_timestamp'),
                'transformation_timestamp': datetime.now().isoformat(),
                'block_range': extracted_data.get('block_range', {}),
                'summary': extracted_data.get('summary', {})
            },
            'transformed_blocks': {},
            'transformed_events': {},
            'analytics': {}
        }
        
        # Transform block data
        if 'latest_block' in extracted_data:
            transformed_data['transformed_blocks'] = self.transform_block_data(
                extracted_data['latest_block']
            )
        
        # Transform events by contract
        events_data = extracted_data.get('events', {})
        
        for contract_name, contract_events in events_data.items():
            if not contract_events:
                continue
            
            # Determine contract type and transform accordingly
            if self._is_erc20_contract(contract_events):
                transformed_data['transformed_events'][contract_name] = self.transform_erc20_events(contract_events)
            elif self._is_uniswap_contract(contract_events):
                transformed_data['transformed_events'][contract_name] = self.transform_uniswap_events(contract_events)
            else:
                # Generic transformation
                transformed_data['transformed_events'][contract_name] = self._transform_generic_events(contract_events)
        
        # Generate cross-contract analytics
        transformed_data['analytics'] = self._generate_analytics(transformed_data)
        
        return transformed_data
    
    def _transform_erc20_transfer(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single ERC20 transfer event"""
        topics = event.get('topics', [])
        data = event.get('data', '0x')
        
        # Extract addresses from topics (last 20 bytes of each topic)
        from_address = '0x' + topics[1][-40:] if len(topics) > 1 else '0x0'
        to_address = '0x' + topics[2][-40:] if len(topics) > 2 else '0x0'
        
        # Extract value from data
        value_hex = data if data.startswith('0x') else '0x' + data
        value_int = int(value_hex, 16) if value_hex != '0x' else 0
        
        return {
            'transaction_hash': event.get('transactionHash'),
            'block_number': event.get('blockNumber'),
            'log_index': event.get('logIndex'),
            'from_address': from_address,
            'to_address': to_address,
            'value_hex': value_hex,
            'value_int': value_int,
            'value_decimal': Decimal(str(value_int)),
            'contract_address': event.get('address'),
            'timestamp': datetime.fromtimestamp(event.get('timestamp', 0)).isoformat() if event.get('timestamp') else None,
            'gas_used': event.get('gasUsed'),
            'gas_price': event.get('gasPrice')
        }
    
    def _transform_uniswap_swap(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Uniswap swap event"""
        topics = event.get('topics', [])
        
        return {
            'transaction_hash': event.get('transactionHash'),
            'block_number': event.get('blockNumber'),
            'pool_id': topics[1] if len(topics) > 1 else None,
            'sender': '0x' + topics[2][-40:] if len(topics) > 2 else None,
            'timestamp': datetime.fromtimestamp(event.get('timestamp', 0)).isoformat() if event.get('timestamp') else None,
            'event_type': 'swap'
        }
    
    def _transform_uniswap_initialize(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Uniswap initialize event"""
        topics = event.get('topics', [])
        
        return {
            'transaction_hash': event.get('transactionHash'),
            'block_number': event.get('blockNumber'),
            'pool_id': topics[1] if len(topics) > 1 else None,
            'timestamp': datetime.fromtimestamp(event.get('timestamp', 0)).isoformat() if event.get('timestamp') else None,
            'event_type': 'initialize'
        }
    
    def _transform_uniswap_liquidity(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Uniswap modify liquidity event"""
        topics = event.get('topics', [])
        
        return {
            'transaction_hash': event.get('transactionHash'),
            'block_number': event.get('blockNumber'),
            'pool_id': topics[1] if len(topics) > 1 else None,
            'sender': '0x' + topics[2][-40:] if len(topics) > 2 else None,
            'timestamp': datetime.fromtimestamp(event.get('timestamp', 0)).isoformat() if event.get('timestamp') else None,
            'event_type': 'modify_liquidity'
        }
    
    def _transform_generic_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform generic contract events"""
        return {
            'events': events,
            'event_count': len(events),
            'transformation_timestamp': datetime.now().isoformat()
        }
    
    def _generate_analytics(self, transformed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cross-contract analytics"""
        analytics = {
            'total_events_processed': 0,
            'contracts_analyzed': len(transformed_data.get('transformed_events', {})),
            'event_distribution': {},
            'temporal_analysis': {
                'time_range_covered': None,
                'peak_activity_periods': []
            }
        }
        
        # Count events by contract
        for contract_name, contract_data in transformed_data.get('transformed_events', {}).items():
            if isinstance(contract_data, dict):
                if 'events' in contract_data:
                    event_count = len(contract_data['events'])
                elif 'swap_events' in contract_data:
                    event_count = (len(contract_data.get('swap_events', [])) + 
                                 len(contract_data.get('initialize_events', [])) +
                                 len(contract_data.get('liquidity_events', [])))
                else:
                    event_count = contract_data.get('event_count', 0)
                
                analytics['event_distribution'][contract_name] = event_count
                analytics['total_events_processed'] += event_count
        
        return analytics
    
    def _is_erc20_transfer(self, event: Dict[str, Any]) -> bool:
        """Check if event is an ERC20 transfer"""
        topics = event.get('topics', [])
        return len(topics) > 0 and topics[0] == EventSignatures.ERC20_TRANSFER
    
    def _is_erc20_contract(self, events: List[Dict[str, Any]]) -> bool:
        """Check if contract events are ERC20"""
        return any(self._is_erc20_transfer(event) for event in events[:5])  # Check first 5 events
    
    def _is_uniswap_contract(self, events: List[Dict[str, Any]]) -> bool:
        """Check if contract events are Uniswap"""
        uniswap_signatures = {
            EventSignatures.UNISWAP_SWAP,
            EventSignatures.UNISWAP_INITIALIZE,
            EventSignatures.UNISWAP_MODIFY_LIQUIDITY
        }
        
        return any(
            event.get('topics', [{}])[0] in uniswap_signatures 
            for event in events[:5]
        )
    
    def _get_utilization_status(self, utilization: float) -> str:
        """Get network utilization status"""
        if utilization < 50:
            return "low"
        elif utilization < 80:
            return "moderate"
        elif utilization < 95:
            return "high"
        else:
            return "critical"
    
    def save_transformed_data(self, data: Dict[str, Any], output_file: str = None):
        """Save transformed data to file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"transformed_data_{timestamp}.json"
        
        logger.info(f"Saving transformed data to {output_file}")
        
        # Custom JSON encoder for Decimal
        def decimal_encoder(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return str(obj)
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=decimal_encoder)
        
        logger.info(f"Transformed data saved to {output_file}")


async def main():
    """Main entry point for data transformation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Transform Ethereum blockchain data")
    parser.add_argument("input_file", help="Input JSON file with extracted data")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--erc20-only", action="store_true", help="Transform only ERC20 events")
    parser.add_argument("--uniswap-only", action="store_true", help="Transform only Uniswap events")
    
    args = parser.parse_args()
    
    try:
        # Load input data
        logger.info(f"Loading data from {args.input_file}")
        with open(args.input_file, 'r') as f:
            extracted_data = json.load(f)
        
        transformer = DataTransformer()
        
        if args.erc20_only:
            # Transform only ERC20 events
            all_erc20_events = []
            for contract_events in extracted_data.get('events', {}).values():
                all_erc20_events.extend([e for e in contract_events if transformer._is_erc20_transfer(e)])
            
            transformed_data = transformer.transform_erc20_events(all_erc20_events)
        elif args.uniswap_only:
            # Transform only Uniswap events
            all_uniswap_events = []
            for contract_events in extracted_data.get('events', {}).values():
                all_uniswap_events.extend([e for e in contract_events if transformer._is_uniswap_contract([e])])
            
            transformed_data = transformer.transform_uniswap_events(all_uniswap_events)
        else:
            # Transform all data
            transformed_data = transformer.transform_extracted_data(extracted_data)
        
        # Save transformed data
        transformer.save_transformed_data(transformed_data, args.output)
        
        logger.info("Data transformation completed successfully")
        
    except Exception as e:
        logger.error(f"Data transformation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())