"""
Event models for Ethereum blockchain events
Python equivalent of Java model classes
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from decimal import Decimal


class EthereumEvent(BaseModel):
    """Base class for all Ethereum events (equivalent to Java EthereumEvent)"""
    event_name: str
    contract_address: str
    block_number: int
    transaction_hash: str
    log_index: int
    timestamp: datetime
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ERC20TransferEvent(EthereumEvent):
    """ERC20 Transfer event (equivalent to Java ERC20TransferEvent)"""
    from_address: str
    to_address: str
    value: Decimal
    token_symbol: Optional[str] = None
    token_decimals: Optional[int] = None
    
    def __init__(self, **data):
        if 'event_name' not in data:
            data['event_name'] = 'Transfer'
        super().__init__(**data)


class UniswapSwapEvent(EthereumEvent):
    """Uniswap V4 Swap event (equivalent to Java UniswapSwapEvent)"""
    pool_id: str
    sender: str
    amount_0: int  # int128 in Solidity
    amount_1: int  # int128 in Solidity
    sqrt_price_x96: int  # uint160 in Solidity
    liquidity: int  # uint128 in Solidity
    tick: int  # int24 in Solidity
    
    # Topic signature for Uniswap V4 Swap event
    TOPIC_0 = "0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9"
    
    def __init__(self, **data):
        if 'event_name' not in data:
            data['event_name'] = 'Swap'
        super().__init__(**data)


class UniswapInitializeEvent(EthereumEvent):
    """Uniswap V4 Initialize event (equivalent to Java UniswapInitializeEvent)"""
    pool_id: str
    currency0: str
    currency1: str
    fee: int  # uint24 in Solidity
    tick_spacing: int  # int24 in Solidity
    hooks: str
    
    # Topic signature for Uniswap V4 Initialize event
    TOPIC_0 = "0x98636036cb66a9c19a37435efc1e90142190214e8abeb821bdda3f2990dd4c95"
    
    def __init__(self, **data):
        if 'event_name' not in data:
            data['event_name'] = 'Initialize'
        super().__init__(**data)


class UniswapModifyLiquidityEvent(EthereumEvent):
    """Uniswap V4 ModifyLiquidity event (equivalent to Java UniswapModifyLiquidityEvent)"""
    pool_id: str
    sender: str
    tick_lower: int  # int24 in Solidity
    tick_upper: int  # int24 in Solidity
    liquidity_delta: int  # int256 in Solidity
    
    # Topic signature for Uniswap V4 ModifyLiquidity event
    TOPIC_0 = "0x3932abb5e2165f7c78ddef6502e29c06225afc2b9a4e51ae1d80f2ed7f6ac1a0"
    
    def __init__(self, **data):
        if 'event_name' not in data:
            data['event_name'] = 'ModifyLiquidity'
        super().__init__(**data)


class BlockEvent(BaseModel):
    """Block event model (equivalent to Java BlockEvent)"""
    block_number: int
    block_hash: str
    parent_hash: str
    timestamp: datetime
    transaction_count: int
    gas_used: int
    gas_limit: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Event signature constants (equivalent to EventSignatureUtil.CommonSignatures)
class EventSignatures:
    """Common Ethereum event signatures"""
    # ERC20 events
    ERC20_TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    ERC20_APPROVAL = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
    
    # ERC721 events
    ERC721_TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    ERC721_APPROVAL = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
    ERC721_APPROVAL_FOR_ALL = "0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31"
    
    # Uniswap V4 events
    UNISWAP_SWAP = UniswapSwapEvent.TOPIC_0
    UNISWAP_INITIALIZE = UniswapInitializeEvent.TOPIC_0
    UNISWAP_MODIFY_LIQUIDITY = UniswapModifyLiquidityEvent.TOPIC_0