package dev.ps.ethblockevents.model;

import java.math.BigInteger;
import java.time.Instant;

/**
 * Represents a Uniswap V4 ModifyLiquidity event
 */
public record UniswapModifyLiquidityEvent(
    String contractAddress,
    byte[] poolId,
    String sender,
    BigInteger tickLower,
    BigInteger tickUpper,
    BigInteger liquidityDelta,
    String transactionHash,
    BigInteger blockNumber,
    BigInteger logIndex,
    Instant timestamp
) {
    // ModifyLiquidity event signature: ModifyLiquidity(bytes32 indexed poolId, address indexed sender, int24 tickLower, int24 tickUpper, int256 liquidityDelta)
    public static final String TOPIC_0 = "0x541c041c2cce48e614b3de043c9280f06b6164c0a1741649e2de3c3d375f7974";
}