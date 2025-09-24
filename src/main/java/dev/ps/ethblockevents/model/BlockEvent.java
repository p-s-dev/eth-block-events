package dev.ps.ethblockevents.model;

import java.math.BigInteger;
import java.time.Instant;
import java.util.List;

public record BlockEvent(
    BigInteger blockNumber,
    String blockHash,
    String parentHash,
    BigInteger gasLimit,
    BigInteger gasUsed,
    Instant timestamp,
    String miner,
    List<String> transactionHashes,
    Integer transactionCount
) {}