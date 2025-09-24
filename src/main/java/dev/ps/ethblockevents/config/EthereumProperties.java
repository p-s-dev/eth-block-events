package dev.ps.ethblockevents.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.List;
import java.util.Map;

@ConfigurationProperties(prefix = "ethereum")
public record EthereumProperties(
    String nodeUrl,
    Long startBlock,
    Integer blockPollingInterval,
    List<ContractConfig> contracts
) {
    
    public record ContractConfig(
        String name,
        String address,
        List<EventConfig> events
    ) {}
    
    public record EventConfig(
        String name,
        String signature,
        List<String> topics,
        boolean enabled
    ) {}
}