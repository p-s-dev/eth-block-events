package dev.ps.ethblockevents.model;

import java.math.BigInteger;
import java.time.Instant;
import java.util.List;
import java.util.Map;

public record EthereumEvent(
    String eventName,
    String contractAddress,
    String transactionHash,
    BigInteger blockNumber,
    BigInteger logIndex,
    Instant timestamp,
    List<String> topics,
    String data,
    Map<String, Object> decodedParameters
) {}