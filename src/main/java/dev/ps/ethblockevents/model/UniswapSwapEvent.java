package dev.ps.ethblockevents.model;

import java.math.BigInteger;
import java.time.Instant;

/**
 * Represents a Uniswap V4 Swap event
 */
public record UniswapSwapEvent(
    String contractAddress,
    byte[] poolId,
    String sender,
    BigInteger amount0,
    BigInteger amount1,
    BigInteger sqrtPriceX96,
    BigInteger liquidity,
    BigInteger tick,
    String transactionHash,
    BigInteger blockNumber,
    BigInteger logIndex,
    Instant timestamp
) {
    // Swap event signature: Swap(bytes32 indexed poolId, address indexed sender, int128 amount0, int128 amount1, uint160 sqrtPriceX96, uint128 liquidity, int24 tick)
    public static final String TOPIC_0 = "0x9cd312f3503782cb1d29f4114896ca5405e9cf41adf9a23b76f74203d292296e";
}