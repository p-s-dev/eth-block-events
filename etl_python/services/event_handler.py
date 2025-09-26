"""
Event handler service
Python equivalent of EventHandlerService
Demonstrates how to handle events published to the EventBus
"""
import logging
from typing import Optional

from ..models.events import (
    EthereumEvent, ERC20TransferEvent, UniswapSwapEvent,
    UniswapInitializeEvent, UniswapModifyLiquidityEvent, BlockEvent
)
from ..services.event_bus import subscribe, get_event_bus

logger = logging.getLogger(__name__)


class EventHandlerService:
    """
    Example service that demonstrates how to handle events published to the EventBus
    Python equivalent of Java EventHandlerService
    """
    
    def __init__(self):
        self.event_bus = get_event_bus()
        
    def initialize(self):
        """Initialize the service and register with event bus"""
        self.event_bus.register(self)
        logger.info("Event handler service registered with EventBus")
    
    @subscribe(EthereumEvent)
    def handle_ethereum_event(self, event: EthereumEvent):
        """Handle generic Ethereum events"""
        logger.info(
            f"Received Ethereum event: {event.event_name} from contract: {event.contract_address} "
            f"in block: {event.block_number}"
        )
        
        # Add your custom logic here to handle generic Ethereum events
        # For example: store in database, send notifications, trigger other processes, etc.
        self._process_generic_event(event)
    
    @subscribe(ERC20TransferEvent)
    def handle_erc20_transfer_event(self, event: ERC20TransferEvent):
        """Handle ERC20 Transfer events"""
        logger.info(
            f"ERC20 Transfer: {event.value} {event.token_symbol or 'tokens'} "
            f"from {event.from_address} to {event.to_address} "
            f"(Block: {event.block_number}, Tx: {event.transaction_hash})"
        )
        
        # Add custom logic for ERC20 transfers
        # Examples:
        # - Track large transfers
        # - Monitor specific addresses
        # - Calculate volume metrics
        # - Store in database
        self._process_erc20_transfer(event)
    
    @subscribe(BlockEvent)
    def handle_block_event(self, event: BlockEvent):
        """Handle new block events"""
        logger.info(
            f"New Block: #{event.block_number} ({event.block_hash[:10]}...) "
            f"with {event.transaction_count} transactions, "
            f"Gas Used: {event.gas_used:,}/{event.gas_limit:,}"
        )
        
        # Add custom logic for new blocks
        # Examples:
        # - Track network activity
        # - Monitor gas prices
        # - Calculate network metrics
        # - Trigger periodic tasks
        self._process_block_event(event)
    
    @subscribe(UniswapSwapEvent) 
    def handle_uniswap_swap_event(self, event: UniswapSwapEvent):
        """Handle Uniswap V4 Swap events"""
        logger.info(
            f"Uniswap Swap: Pool {event.pool_id[:10]}... "
            f"Amount0: {event.amount_0}, Amount1: {event.amount_1} "
            f"(Block: {event.block_number})"
        )
        
        # Add custom logic for Uniswap swaps
        # Examples:
        # - Track trading volume
        # - Monitor price movements
        # - Detect arbitrage opportunities
        # - Calculate liquidity metrics
        self._process_uniswap_swap(event)
    
    @subscribe(UniswapInitializeEvent)
    def handle_uniswap_initialize_event(self, event: UniswapInitializeEvent):
        """Handle Uniswap V4 Initialize events"""
        logger.info(
            f"Uniswap Pool Initialized: {event.pool_id[:10]}... "
            f"Currency0: {event.currency0}, Currency1: {event.currency1} "
            f"Fee: {event.fee} (Block: {event.block_number})"
        )
        
        # Add custom logic for new pool initialization
        # Examples:
        # - Track new trading pairs
        # - Monitor pool creation patterns
        # - Set up automated monitoring
        # - Store pool configurations
        self._process_uniswap_initialize(event)
    
    @subscribe(UniswapModifyLiquidityEvent)
    def handle_uniswap_modify_liquidity_event(self, event: UniswapModifyLiquidityEvent):
        """Handle Uniswap V4 ModifyLiquidity events"""
        action = "Added" if event.liquidity_delta > 0 else "Removed"
        logger.info(
            f"Uniswap Liquidity {action}: Pool {event.pool_id[:10]}... "
            f"Delta: {event.liquidity_delta} "
            f"Ticks: [{event.tick_lower}, {event.tick_upper}] "
            f"(Block: {event.block_number})"
        )
        
        # Add custom logic for liquidity changes
        # Examples:
        # - Track liquidity providers
        # - Monitor liquidity depth
        # - Calculate yield farming metrics
        # - Detect liquidity migrations
        self._process_uniswap_modify_liquidity(event)
    
    def _process_generic_event(self, event: EthereumEvent):
        """Process generic Ethereum event - extend with custom logic"""
        # Example: Could store to database, send to external API, etc.
        pass
    
    def _process_erc20_transfer(self, event: ERC20TransferEvent):
        """Process ERC20 transfer event - extend with custom logic"""
        # Example implementations:
        
        # Track large transfers (> $10,000 equivalent)
        if event.value > 10000 * 10**18:  # Assuming 18 decimals
            logger.warning(f"Large transfer detected: {event.value}")
        
        # Monitor specific addresses
        important_addresses = {
            "0x..." : "Exchange Hot Wallet",
            "0x..." : "DeFi Protocol"
        }
        
        if event.from_address in important_addresses:
            logger.info(f"Transfer from {important_addresses[event.from_address]}")
        
        if event.to_address in important_addresses:
            logger.info(f"Transfer to {important_addresses[event.to_address]}")
    
    def _process_block_event(self, event: BlockEvent):
        """Process block event - extend with custom logic"""
        # Example: Track network congestion
        utilization = (event.gas_used / event.gas_limit) * 100
        if utilization > 90:
            logger.warning(f"High network utilization: {utilization:.1f}%")
    
    def _process_uniswap_swap(self, event: UniswapSwapEvent):
        """Process Uniswap swap event - extend with custom logic"""
        # Example: Could calculate USD values, track arbitrage, etc.
        pass
    
    def _process_uniswap_initialize(self, event: UniswapInitializeEvent):
        """Process Uniswap initialize event - extend with custom logic"""
        # Example: Could setup monitoring for new pool, fetch token info, etc.
        pass
    
    def _process_uniswap_modify_liquidity(self, event: UniswapModifyLiquidityEvent):
        """Process Uniswap modify liquidity event - extend with custom logic"""
        # Example: Could track LP positions, calculate APY, etc.
        pass


# Utility function to create bytes hex representation (equivalent to Java bytesToHex)
def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hex string representation"""
    return "0x" + data.hex()