package dev.ps.ethblockevents.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.List;
import java.util.Map;

@ConfigurationProperties(prefix = "ethereum")
public record EthereumProperties(
    String nodeUrl,
    String websocketUrl,
    Long startBlock,
    Integer blockPollingInterval,
    List<ContractConfig> contracts
) {
    
    public record ContractConfig(
        String name,
        String address,
        List<EventConfig> events,
        BlockRange blockRange  // New field for block range filtering
    ) {}
    
    public record EventConfig(
        String name,
        String signature,
        List<String> topics,
        boolean enabled
    ) {}
    
    /**
     * Block range configuration for event filtering
     */
    public record BlockRange(
        Long fromBlock,  // null means "latest"
        Long toBlock     // null means "latest" or continuous listening
    ) {
        public static final BlockRange LATEST = new BlockRange(null, null);
        public static final BlockRange ALL = new BlockRange(0L, null);
    }
}