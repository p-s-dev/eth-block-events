package dev.ps.ethblockevents.service;

import dev.ps.ethblockevents.config.EthereumProperties;
import org.web3j.protocol.core.methods.response.Log;

/**
 * Generic interface for contract event listeners that can be extended for specific contract types
 */
public interface GenericContractEventListener {
    
    /**
     * Handles a generic log event and can perform specific processing based on the event type
     * 
     * @param log The raw log event from the blockchain
     * @param contractConfig The contract configuration
     * @param eventConfig The event configuration
     * @return true if the event was handled, false otherwise
     */
    boolean handleEvent(Log log, EthereumProperties.ContractConfig contractConfig, 
                       EthereumProperties.EventConfig eventConfig);
    
    /**
     * Returns true if this listener can handle events for the given contract
     * 
     * @param contractConfig The contract configuration
     * @return true if this listener supports the contract
     */
    boolean supportsContract(EthereumProperties.ContractConfig contractConfig);
    
    /**
     * Returns the priority of this listener (higher values are processed first)
     * 
     * @return priority value
     */
    default int getPriority() {
        return 0;
    }
}