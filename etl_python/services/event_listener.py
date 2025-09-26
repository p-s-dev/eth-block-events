"""
Ethereum event listener service
Python equivalent of EthereumEventListenerService
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from web3 import Web3
from web3.types import LogReceipt

from ..models.events import (
    EthereumEvent, ERC20TransferEvent, UniswapSwapEvent, 
    UniswapInitializeEvent, UniswapModifyLiquidityEvent, EventSignatures
)
from ..services.event_bus import get_event_bus
from ..services.ethereum_client import EthereumClient
from ..config import ContractConfig, EventConfig

logger = logging.getLogger(__name__)


class EventListenerService:
    """
    Main service for listening to Ethereum contract events
    Python equivalent of EthereumEventListenerService
    """
    
    def __init__(self, ethereum_client: EthereumClient, contracts: List[ContractConfig]):
        self.ethereum_client = ethereum_client
        self.contracts = contracts
        self.event_bus = get_event_bus()
        self.web3 = ethereum_client.get_web3()
        self.web3_ws = ethereum_client.get_web3_websocket()
        
        # Store active filters for cleanup
        self.active_filters = []
        
        logger.info(f"Initialized EventListenerService with {len(contracts)} contracts")
    
    async def start_listening(self):
        """
        Start listening to all configured contract events
        Equivalent to startListening method in Java
        """
        logger.info("Starting Ethereum event listener service")
        
        # Start listening to each contract
        for contract in self.contracts:
            await self._subscribe_to_contract_events(contract)
        
        # Start the event listening loop
        if self.web3_ws and self.active_filters:
            await self._event_listening_loop()
        else:
            logger.warning("No WebSocket connection or filters available")
    
    async def _subscribe_to_contract_events(self, contract: ContractConfig):
        """
        Subscribe to events for a specific contract
        Equivalent to subscribeToContractEvents in Java
        """
        logger.info(f"Subscribing to events for contract: {contract.name} ({contract.address})")
        
        if not self.web3_ws:
            logger.warning(f"WebSocket not available, skipping contract {contract.name}")
            return
        
        # Create filters for each enabled event
        for event_config in contract.events:
            if event_config.enabled:
                try:
                    event_filter = self._create_event_filter(contract, event_config)
                    if event_filter:
                        self.active_filters.append({
                            'filter': event_filter,
                            'contract': contract,
                            'event_config': event_config
                        })
                        logger.info(f"Created filter for {contract.name}.{event_config.name}")
                except Exception as e:
                    logger.error(f"Failed to create filter for {contract.name}.{event_config.name}: {e}")
    
    def _create_event_filter(self, contract: ContractConfig, event_config: EventConfig):
        """Create a Web3 event filter"""
        try:
            filter_params = {
                'address': contract.address,
                'topics': [event_config.signature] + event_config.topics
            }
            
            return self.web3_ws.eth.filter(filter_params)
        except Exception as e:
            logger.error(f"Error creating event filter: {e}")
            return None
    
    async def _event_listening_loop(self):
        """
        Main event listening loop
        Continuously checks for new events and processes them
        """
        logger.info("Starting event listening loop")
        
        while True:
            try:
                for filter_info in self.active_filters:
                    try:
                        # Get new events from this filter
                        new_events = filter_info['filter'].get_new_entries()
                        
                        for log_entry in new_events:
                            await self._handle_log_event(
                                log_entry, 
                                filter_info['contract'], 
                                filter_info['event_config']
                            )
                    
                    except Exception as e:
                        logger.error(f"Error processing filter events: {e}")
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error in event listening loop: {e}")
                await asyncio.sleep(5)  # Longer delay on error
    
    async def _handle_log_event(self, log: LogReceipt, contract: ContractConfig, event_config: EventConfig):
        """
        Handle a single log event
        Equivalent to handleEvent methods in Java
        """
        try:
            # Get block timestamp
            timestamp = self.ethereum_client.get_block_timestamp(log['blockNumber'])
            
            # Create appropriate event object based on event signature
            event_signature = log['topics'][0].hex()
            
            if event_signature == EventSignatures.ERC20_TRANSFER:
                event = self._create_erc20_transfer_event(log, contract, timestamp)
            elif event_signature == EventSignatures.UNISWAP_SWAP:
                event = self._create_uniswap_swap_event(log, contract, timestamp)
            elif event_signature == EventSignatures.UNISWAP_INITIALIZE:
                event = self._create_uniswap_initialize_event(log, contract, timestamp)
            elif event_signature == EventSignatures.UNISWAP_MODIFY_LIQUIDITY:
                event = self._create_uniswap_modify_liquidity_event(log, contract, timestamp)
            else:
                # Generic ethereum event
                event = self._create_generic_event(log, contract, event_config, timestamp)
            
            # Publish event to event bus
            await self.event_bus.post_async(event)
            
            logger.debug(f"Processed {event.event_name} event from {contract.name}")
            
        except Exception as e:
            logger.error(f"Error handling log event: {e}", exc_info=True)
    
    def _create_erc20_transfer_event(self, log: LogReceipt, contract: ContractConfig, timestamp: datetime) -> ERC20TransferEvent:
        """Create ERC20 Transfer event from log data"""
        topics = log['topics']
        data = log['data']
        
        # Decode ERC20 Transfer event
        # topics[1] = from address, topics[2] = to address
        # data = value (uint256)
        from_address = self.web3.to_checksum_address(topics[1][-20:])  # Last 20 bytes
        to_address = self.web3.to_checksum_address(topics[2][-20:])    # Last 20 bytes
        value = int(data.hex(), 16) if data else 0
        
        return ERC20TransferEvent(
            contract_address=contract.address,
            block_number=log['blockNumber'],
            transaction_hash=log['transactionHash'].hex(),
            log_index=log['logIndex'],
            timestamp=timestamp,
            from_address=from_address,
            to_address=to_address,
            value=Decimal(value),
            token_symbol=contract.name,  # Use contract name as symbol
            raw_data=dict(log)
        )
    
    def _create_uniswap_swap_event(self, log: LogReceipt, contract: ContractConfig, timestamp: datetime) -> UniswapSwapEvent:
        """Create Uniswap Swap event from log data"""
        topics = log['topics']
        data = log['data']
        
        # This is a simplified version - actual decoding would need proper ABI
        pool_id = topics[1].hex() if len(topics) > 1 else "0x"
        sender = self.web3.to_checksum_address(topics[2][-20:]) if len(topics) > 2 else "0x0"
        
        # For simplicity, using placeholder values - real implementation would decode data properly
        return UniswapSwapEvent(
            contract_address=contract.address,
            block_number=log['blockNumber'],
            transaction_hash=log['transactionHash'].hex(),
            log_index=log['logIndex'],
            timestamp=timestamp,
            pool_id=pool_id,
            sender=sender,
            amount_0=0,  # Would decode from data
            amount_1=0,  # Would decode from data
            sqrt_price_x96=0,  # Would decode from data
            liquidity=0,  # Would decode from data
            tick=0,  # Would decode from data
            raw_data=dict(log)
        )
    
    def _create_uniswap_initialize_event(self, log: LogReceipt, contract: ContractConfig, timestamp: datetime) -> UniswapInitializeEvent:
        """Create Uniswap Initialize event from log data"""
        topics = log['topics']
        
        pool_id = topics[1].hex() if len(topics) > 1 else "0x"
        
        return UniswapInitializeEvent(
            contract_address=contract.address,
            block_number=log['blockNumber'],
            transaction_hash=log['transactionHash'].hex(),
            log_index=log['logIndex'],
            timestamp=timestamp,
            pool_id=pool_id,
            currency0="0x0",  # Would decode from data
            currency1="0x0",  # Would decode from data
            fee=0,  # Would decode from data
            tick_spacing=0,  # Would decode from data
            hooks="0x0",  # Would decode from data
            raw_data=dict(log)
        )
    
    def _create_uniswap_modify_liquidity_event(self, log: LogReceipt, contract: ContractConfig, timestamp: datetime) -> UniswapModifyLiquidityEvent:
        """Create Uniswap ModifyLiquidity event from log data"""
        topics = log['topics']
        
        pool_id = topics[1].hex() if len(topics) > 1 else "0x"
        sender = self.web3.to_checksum_address(topics[2][-20:]) if len(topics) > 2 else "0x0"
        
        return UniswapModifyLiquidityEvent(
            contract_address=contract.address,
            block_number=log['blockNumber'],
            transaction_hash=log['transactionHash'].hex(),
            log_index=log['logIndex'],
            timestamp=timestamp,
            pool_id=pool_id,
            sender=sender,
            tick_lower=0,  # Would decode from data
            tick_upper=0,  # Would decode from data
            liquidity_delta=0,  # Would decode from data
            raw_data=dict(log)
        )
    
    def _create_generic_event(self, log: LogReceipt, contract: ContractConfig, 
                            event_config: EventConfig, timestamp: datetime) -> EthereumEvent:
        """Create generic Ethereum event from log data"""
        return EthereumEvent(
            event_name=event_config.name,
            contract_address=contract.address,
            block_number=log['blockNumber'],
            transaction_hash=log['transactionHash'].hex(),
            log_index=log['logIndex'],
            timestamp=timestamp,
            raw_data=dict(log)
        )
    
    def stop_listening(self):
        """Stop all event listeners and clean up filters"""
        logger.info("Stopping event listeners")
        
        for filter_info in self.active_filters:
            try:
                if self.web3_ws:
                    self.web3_ws.eth.uninstall_filter(filter_info['filter'].filter_id)
            except Exception as e:
                logger.error(f"Error uninstalling filter: {e}")
        
        self.active_filters.clear()
        logger.info("Event listeners stopped")