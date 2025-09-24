package dev.ps.ethblockevents.model;

import java.math.BigInteger;
import java.time.Instant;

/**
 * Represents a Uniswap V4 Initialize event
 */
public record UniswapInitializeEvent(
    String contractAddress,
    byte[] poolId,
    String currency0,
    String currency1,
    BigInteger fee,
    BigInteger tickSpacing,
    String hooks,
    String transactionHash,
    BigInteger blockNumber,
    BigInteger logIndex,
    Instant timestamp
) {
    // Initialize event signature: Initialize(bytes32 indexed poolId, address indexed currency0, address indexed currency1, uint24 fee, int24 tickSpacing, address hooks)
    public static final String TOPIC_0 = "0x3fd553db44f207b1f41348cfc4d251860814af9eadc470e8e7895e4d120511f4";
}