package dev.ps.ethblockevents.service;

import com.google.common.eventbus.EventBus;
import dev.ps.ethblockevents.config.EthereumProperties;
import dev.ps.ethblockevents.model.BlockEvent;
import dev.ps.ethblockevents.model.ERC20TransferEvent;
import dev.ps.ethblockevents.model.EthereumEvent;
import io.reactivex.disposables.Disposable;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.DefaultBlockParameter;
import org.web3j.protocol.core.DefaultBlockParameterName;
import org.web3j.protocol.core.methods.request.EthFilter;
import org.web3j.protocol.core.methods.response.EthBlock;
import org.web3j.protocol.core.methods.response.Log;

import java.math.BigInteger;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Service
public class EthereumEventListenerService {

    private static final Logger logger = LoggerFactory.getLogger(EthereumEventListenerService.class);

    private final Web3j web3j;
    private final Web3j web3jWebsocket;
    private final EventBus eventBus;
    private final EthereumProperties ethereumProperties;
    private final Map<String, Disposable> subscriptions = new ConcurrentHashMap<>();
    private final List<GenericContractEventListener> eventListeners;

    public EthereumEventListenerService(Web3j web3j, 
                                      @Qualifier("web3jWebsocket") Web3j web3jWebsocket,
                                      EventBus eventBus, 
                                      EthereumProperties ethereumProperties,
                                      List<GenericContractEventListener> eventListeners) {
        this.web3j = web3j;
        this.web3jWebsocket = web3jWebsocket;
        this.eventBus = eventBus;
        this.ethereumProperties = ethereumProperties;
        this.eventListeners = eventListeners.stream()
            .sorted((a, b) -> Integer.compare(b.getPriority(), a.getPriority()))
            .collect(Collectors.toList());
    }

    @PostConstruct
    public void startListening() {
        logger.info("Starting Ethereum event listener service");
        
        if (ethereumProperties.contracts() != null) {
            ethereumProperties.contracts().forEach(this::subscribeToContractEvents);
        }
        
        // Start listening to block events via WebSocket
        startBlockListening();
    }

    @PreDestroy
    public void stopListening() {
        logger.info("Stopping Ethereum event listener service");
        subscriptions.values().forEach(Disposable::dispose);
        subscriptions.clear();
    }

    public void startBlockListening() {
        if (ethereumProperties.websocketUrl() == null || 
            ethereumProperties.websocketUrl().trim().isEmpty()) {
            logger.info("WebSocket URL not configured, skipping block event listener");
            return;
        }
        
        try {
            logger.info("Starting block event listener via WebSocket");
            
            Disposable blockSubscription = web3jWebsocket.blockFlowable(false)
                .subscribe(
                    this::handleBlockEvent,
                    error -> logger.error("Error in block subscription: {}", error.getMessage(), error)
                );
            
            subscriptions.put("block_listener", blockSubscription);
            logger.info("Successfully subscribed to block events");
            
        } catch (Exception e) {
            logger.error("Failed to start block listening: {}", e.getMessage(), e);
        }
    }

    void handleBlockEvent(EthBlock ethBlock) {
        try {
            EthBlock.Block block = ethBlock.getBlock();
            if (block == null) {
                return;
            }
            
            logger.debug("Received new block: {} with {} transactions", 
                        block.getNumber(), block.getTransactions().size());
            
            List<String> transactionHashes = block.getTransactions().stream()
                .map(tx -> {
                    if (tx instanceof EthBlock.TransactionHash) {
                        return ((EthBlock.TransactionHash) tx).get();
                    } else if (tx instanceof EthBlock.TransactionObject) {
                        return ((EthBlock.TransactionObject) tx).get().getHash();
                    }
                    return tx.toString();
                })
                .collect(Collectors.toList());
            
            BlockEvent blockEvent = new BlockEvent(
                block.getNumber(),
                block.getHash(),
                block.getParentHash(),
                block.getGasLimit(),
                block.getGasUsed(),
                Instant.ofEpochSecond(block.getTimestamp().longValue()),
                block.getMiner(),
                transactionHashes,
                block.getTransactions().size()
            );
            
            eventBus.post(blockEvent);
            logger.info("Published block event for block: {} with {} transactions", 
                       block.getNumber(), block.getTransactions().size());
            
        } catch (Exception e) {
            logger.error("Error handling block event: {}", e.getMessage(), e);
        }
    }

    private void subscribeToContractEvents(EthereumProperties.ContractConfig contractConfig) {
        if (contractConfig.events() == null || contractConfig.events().isEmpty()) {
            return;
        }

        logger.info("Subscribing to events for contract: {} at address: {}", 
                   contractConfig.name(), contractConfig.address());

        contractConfig.events().stream()
                .filter(EthereumProperties.EventConfig::enabled)
                .forEach(eventConfig -> subscribeToEvent(contractConfig, eventConfig));
    }

    private void subscribeToEvent(EthereumProperties.ContractConfig contractConfig, 
                                 EthereumProperties.EventConfig eventConfig) {
        
        try {
            // Determine block range for the filter
            EthereumProperties.BlockRange blockRange = contractConfig.blockRange();
            DefaultBlockParameter fromBlock = getFromBlockParameter(blockRange);
            DefaultBlockParameter toBlock = getToBlockParameter(blockRange);
            
            EthFilter filter = new EthFilter(
                fromBlock,
                toBlock,
                contractConfig.address()
            );

            // Add event signature as first topic
            if (eventConfig.signature() != null && !eventConfig.signature().isEmpty()) {
                filter.addSingleTopic(eventConfig.signature());
            }

            // Add additional topics if specified
            if (eventConfig.topics() != null) {
                eventConfig.topics().forEach(filter::addSingleTopic);
            }

            String subscriptionKey = contractConfig.address() + "_" + eventConfig.name();
            
            Disposable subscription = web3j.ethLogFlowable(filter)
                .subscribe(
                    log -> handleLogEvent(log, contractConfig, eventConfig),
                    error -> logger.error("Error in subscription for {}: {}", subscriptionKey, error.getMessage(), error)
                );

            subscriptions.put(subscriptionKey, subscription);
            logger.info("Successfully subscribed to event: {} for contract: {} (blocks: {} to {})", 
                       eventConfig.name(), contractConfig.name(), fromBlock, toBlock);

        } catch (Exception e) {
            logger.error("Failed to subscribe to event: {} for contract: {}", 
                        eventConfig.name(), contractConfig.name(), e);
        }
    }

    private void handleLogEvent(Log log, EthereumProperties.ContractConfig contractConfig, 
                               EthereumProperties.EventConfig eventConfig) {
        try {
            logger.debug("Received log event: {} for contract: {}", eventConfig.name(), contractConfig.name());

            // First, try specialized listeners
            boolean handled = false;
            for (GenericContractEventListener listener : eventListeners) {
                if (listener.supportsContract(contractConfig)) {
                    handled = listener.handleEvent(log, contractConfig, eventConfig);
                    if (handled) {
                        logger.debug("Event handled by specialized listener: {}", listener.getClass().getSimpleName());
                        break;
                    }
                }
            }

            // If no specialized listener handled it, create a generic event
            if (!handled) {
                // Get block timestamp
                Instant timestamp = getBlockTimestamp(log.getBlockNumber());

                // Create generic Ethereum event
                EthereumEvent ethereumEvent = new EthereumEvent(
                    eventConfig.name(),
                    log.getAddress(),
                    log.getTransactionHash(),
                    log.getBlockNumber(),
                    log.getLogIndex(),
                    timestamp,
                    log.getTopics(),
                    log.getData(),
                    Collections.emptyMap() // TODO: Implement parameter decoding
                );

                // Publish to EventBus
                eventBus.post(ethereumEvent);
                logger.info("Published generic Ethereum event: {} for contract: {}", 
                           eventConfig.name(), contractConfig.name());
            }

            // Handle specific legacy event types (for backward compatibility)
            if ("Transfer".equals(eventConfig.name()) && isERC20TransferEvent(log)) {
                handleERC20TransferEvent(log);
            }

        } catch (Exception e) {
            logger.error("Error handling log event: {}", e.getMessage(), e);
        }
    }

    private boolean isERC20TransferEvent(Log log) {
        return log.getTopics().size() >= 1 && 
               ERC20TransferEvent.TOPIC_0.equals(log.getTopics().get(0));
    }

    private void handleERC20TransferEvent(Log log) {
        try {
            if (log.getTopics().size() < 3) {
                logger.warn("Invalid ERC20 Transfer event - not enough topics");
                return;
            }

            String from = "0x" + log.getTopics().get(1).substring(26);
            String to = "0x" + log.getTopics().get(2).substring(26);
            
            // Decode value from data
            BigInteger value = BigInteger.ZERO;
            if (log.getData() != null && !log.getData().equals("0x")) {
                try {
                    value = new BigInteger(log.getData().substring(2), 16);
                } catch (NumberFormatException e) {
                    logger.warn("Failed to decode transfer value: {}", e.getMessage());
                }
            }

            ERC20TransferEvent transferEvent = new ERC20TransferEvent(
                log.getAddress(),
                from,
                to,
                value,
                log.getTransactionHash(),
                log.getBlockNumber(),
                log.getLogIndex()
            );

            eventBus.post(transferEvent);
            logger.info("Published ERC20 Transfer event: {} tokens from {} to {} in tx: {}", 
                       value, from, to, log.getTransactionHash());

        } catch (Exception e) {
            logger.error("Error handling ERC20 Transfer event: {}", e.getMessage(), e);
        }
    }

    private Instant getBlockTimestamp(BigInteger blockNumber) {
        try {
            EthBlock ethBlock = web3j.ethGetBlockByNumber(
                org.web3j.protocol.core.DefaultBlockParameter.valueOf(blockNumber), false
            ).send();
            
            if (ethBlock.getBlock() != null) {
                return Instant.ofEpochSecond(ethBlock.getBlock().getTimestamp().longValue());
            }
        } catch (Exception e) {
            logger.warn("Failed to get block timestamp for block {}: {}", blockNumber, e.getMessage());
        }
        return Instant.now();
    }
    
    /**
     * Determines the from block parameter based on block range configuration
     */
    private DefaultBlockParameter getFromBlockParameter(EthereumProperties.BlockRange blockRange) {
        if (blockRange == null || blockRange.fromBlock() == null) {
            return DefaultBlockParameterName.LATEST;
        }
        return DefaultBlockParameter.valueOf(BigInteger.valueOf(blockRange.fromBlock()));
    }
    
    /**
     * Determines the to block parameter based on block range configuration
     */
    private DefaultBlockParameter getToBlockParameter(EthereumProperties.BlockRange blockRange) {
        if (blockRange == null || blockRange.toBlock() == null) {
            return DefaultBlockParameterName.LATEST;
        }
        return DefaultBlockParameter.valueOf(BigInteger.valueOf(blockRange.toBlock()));
    }
    
    /**
     * Dynamically add a contract to monitoring at runtime
     */
    public void addDynamicContract(EthereumProperties.ContractConfig contractConfig) {
        logger.info("Dynamically adding contract: {} at {}", contractConfig.name(), contractConfig.address());
        subscribeToContractEvents(contractConfig);
    }
}