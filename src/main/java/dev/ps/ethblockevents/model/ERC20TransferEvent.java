package dev.ps.ethblockevents.model;

import java.math.BigInteger;

/**
 * Specific event model for ERC20 Transfer events
 */
public record ERC20TransferEvent(
    String contractAddress,
    String from,
    String to,
    BigInteger value,
    String transactionHash,
    BigInteger blockNumber,
    BigInteger logIndex
) {
    
    public static final String EVENT_SIGNATURE = "Transfer(address,address,uint256)";
    public static final String TOPIC_0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";
}