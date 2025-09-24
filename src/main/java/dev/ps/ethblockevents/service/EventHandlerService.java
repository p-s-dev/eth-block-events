package dev.ps.ethblockevents.service;

import com.google.common.eventbus.EventBus;
import com.google.common.eventbus.Subscribe;
import dev.ps.ethblockevents.model.ERC20TransferEvent;
import dev.ps.ethblockevents.model.EthereumEvent;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/**
 * Example service that demonstrates how to handle events published to the EventBus
 */
@Service
public class EventHandlerService {

    private static final Logger logger = LoggerFactory.getLogger(EventHandlerService.class);

    private final EventBus eventBus;

    public EventHandlerService(EventBus eventBus) {
        this.eventBus = eventBus;
    }

    @PostConstruct
    public void initialize() {
        eventBus.register(this);
        logger.info("Event handler service registered with EventBus");
    }

    @Subscribe
    public void handleEthereumEvent(EthereumEvent event) {
        logger.info("Received Ethereum event: {} from contract: {} in block: {}", 
                   event.eventName(), 
                   event.contractAddress(), 
                   event.blockNumber());
        
        // Add your custom logic here to handle generic Ethereum events
        // For example: store in database, send notifications, trigger other processes, etc.
    }

    @Subscribe
    public void handleERC20TransferEvent(ERC20TransferEvent event) {
        logger.info("Received ERC20 Transfer: {} tokens from {} to {} (contract: {}, tx: {})", 
                   event.value(), 
                   event.from(), 
                   event.to(),
                   event.contractAddress(),
                   event.transactionHash());
        
        // Add your custom logic here to handle ERC20 transfer events
        // For example: update balances, trigger alerts for large transfers, etc.
    }
}