"""
Ethereum client service
Python equivalent of Web3j configuration and usage
"""
import logging
from typing import Optional, Dict, Any, List
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers import HTTPProvider, WebsocketProvider
from web3.exceptions import Web3Exception
import asyncio
from datetime import datetime

from ..models.events import BlockEvent
from ..services.event_bus import get_event_bus

logger = logging.getLogger(__name__)


class EthereumClient:
    """
    Ethereum client wrapper
    Python equivalent of Web3j beans in ApplicationConfig
    """
    
    def __init__(self, node_url: str, websocket_url: Optional[str] = None):
        self.node_url = node_url
        self.websocket_url = websocket_url
        self.event_bus = get_event_bus()
        
        # HTTP provider for general queries
        self.web3_http = Web3(HTTPProvider(node_url))
        
        # WebSocket provider for real-time events
        self.web3_ws = None
        if websocket_url:
            try:
                self.web3_ws = Web3(WebsocketProvider(websocket_url))
                logger.info(f"Connected to Ethereum WebSocket: {websocket_url}")
            except Exception as e:
                logger.warning(f"WebSocket connection failed, using HTTP only: {e}")
                
        # Add middleware for PoA networks if needed
        if self.node_url and "goerli" in self.node_url.lower():
            self.web3_http.middleware_onion.inject(geth_poa_middleware, layer=0)
            if self.web3_ws:
                self.web3_ws.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        self._validate_connection()
    
    def _validate_connection(self):
        """Validate connection to Ethereum node"""
        try:
            is_connected = self.web3_http.is_connected()
            if is_connected:
                chain_id = self.web3_http.eth.chain_id
                latest_block = self.web3_http.eth.get_block('latest')
                logger.info(f"Connected to Ethereum network (Chain ID: {chain_id}), Latest block: {latest_block.number}")
            else:
                raise Web3Exception("Failed to connect to Ethereum node")
        except Exception as e:
            logger.error(f"Ethereum connection validation failed: {e}")
            raise
    
    def get_web3(self) -> Web3:
        """Get the HTTP Web3 instance"""
        return self.web3_http
    
    def get_web3_websocket(self) -> Optional[Web3]:
        """Get the WebSocket Web3 instance if available"""
        return self.web3_ws
    
    def get_latest_block_number(self) -> int:
        """Get the latest block number"""
        return self.web3_http.eth.get_block('latest').number
    
    def get_block(self, block_number: int) -> Dict[str, Any]:
        """Get block data by number"""
        return self.web3_http.eth.get_block(block_number, full_transactions=True)
    
    def get_block_timestamp(self, block_number: int) -> datetime:
        """Get block timestamp as datetime"""
        block = self.web3_http.eth.get_block(block_number)
        return datetime.fromtimestamp(block.timestamp)
    
    def create_block_event(self, block_data: Dict[str, Any]) -> BlockEvent:
        """
        Create a BlockEvent from block data
        Equivalent to handleBlockEvent in Java
        """
        return BlockEvent(
            block_number=block_data['number'],
            block_hash=block_data['hash'].hex(),
            parent_hash=block_data['parentHash'].hex(),
            timestamp=datetime.fromtimestamp(block_data['timestamp']),
            transaction_count=len(block_data.get('transactions', [])),
            gas_used=block_data['gasUsed'],
            gas_limit=block_data['gasLimit']
        )
    
    async def start_block_listening(self):
        """
        Start listening to new blocks via WebSocket
        Equivalent to startBlockListening in Java
        """
        if not self.web3_ws:
            logger.warning("WebSocket not available, cannot start block listening")
            return
        
        logger.info("Starting WebSocket block listener")
        
        try:
            # Create filter for new blocks
            block_filter = self.web3_ws.eth.filter('latest')
            
            while True:
                try:
                    # Check for new blocks
                    new_blocks = block_filter.get_new_entries()
                    
                    for block_hash in new_blocks:
                        try:
                            # Get full block data
                            block_data = self.web3_ws.eth.get_block(block_hash, full_transactions=True)
                            
                            # Create and publish block event
                            block_event = self.create_block_event(dict(block_data))
                            await self.event_bus.post_async(block_event)
                            
                            logger.debug(f"Published block event for block {block_data['number']}")
                            
                        except Exception as e:
                            logger.error(f"Error processing block {block_hash.hex()}: {e}")
                
                except Exception as e:
                    logger.error(f"Error in block listening loop: {e}")
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Block listening failed: {e}")
            raise
    
    def get_contract_logs(self, contract_address: str, from_block: int = None, 
                         to_block: int = None, topics: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get contract logs/events
        """
        if from_block is None:
            from_block = self.get_latest_block_number() - 100  # Last 100 blocks by default
        
        if to_block is None:
            to_block = 'latest'
        
        filter_params = {
            'address': contract_address,
            'fromBlock': from_block,
            'toBlock': to_block
        }
        
        if topics:
            filter_params['topics'] = topics
        
        try:
            logs = self.web3_http.eth.get_logs(filter_params)
            return [dict(log) for log in logs]
        except Exception as e:
            logger.error(f"Error getting contract logs: {e}")
            return []