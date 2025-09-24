package dev.ps.ethblockevents.service;

import com.google.common.eventbus.EventBus;
import com.google.common.eventbus.Subscribe;
import dev.ps.ethblockevents.model.BlockEvent;
import dev.ps.ethblockevents.model.ERC20TransferEvent;
import dev.ps.ethblockevents.model.EthereumEvent;
import dev.ps.ethblockevents.model.UniswapInitializeEvent;
import dev.ps.ethblockevents.model.UniswapModifyLiquidityEvent;
import dev.ps.ethblockevents.model.UniswapSwapEvent;
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

    @Subscribe
    public void handleBlockEvent(BlockEvent event) {
        logger.info("Received new block: {} with {} transactions (miner: {}, gas used: {})", 
                   event.blockNumber(), 
                   event.transactionCount(),
                   event.miner(),
                   event.gasUsed());
        
        // Add your custom logic here to handle block events
        // For example: monitor block times, analyze gas usage, track specific miners, etc.
    }
    
    @Subscribe
    public void handleUniswapSwapEvent(UniswapSwapEvent event) {
        logger.info("Received Uniswap Swap: pool {} traded {} <-> {} by {} (tx: {})", 
                   bytesToHex(event.poolId()),
                   event.amount0(), 
                   event.amount1(),
                   event.sender(),
                   event.transactionHash());
        
        // Add your custom logic here to handle Uniswap swap events
        // For example: track trading volumes, analyze price impacts, monitor specific pools, etc.
    }
    
    @Subscribe
    public void handleUniswapInitializeEvent(UniswapInitializeEvent event) {
        logger.info("Received Uniswap Initialize: new pool {} for currencies {} <-> {} (fee: {}, tx: {})", 
                   bytesToHex(event.poolId()),
                   event.currency0(), 
                   event.currency1(),
                   event.fee(),
                   event.transactionHash());
        
        // Add your custom logic here to handle Uniswap pool initialization events
        // For example: track new pools, analyze fee structures, monitor specific currency pairs, etc.
    }
    
    @Subscribe
    public void handleUniswapModifyLiquidityEvent(UniswapModifyLiquidityEvent event) {
        logger.info("Received Uniswap ModifyLiquidity: pool {} liquidity changed by {} (ticks: {}-{}, sender: {}, tx: {})", 
                   bytesToHex(event.poolId()),
                   event.liquidityDelta(),
                   event.tickLower(),
                   event.tickUpper(),
                   event.sender(),
                   event.transactionHash());
        
        // Add your custom logic here to handle Uniswap liquidity modification events
        // For example: track liquidity changes, analyze LP activity, monitor specific ranges, etc.
    }
    
    private String bytesToHex(byte[] bytes) {
        StringBuilder result = new StringBuilder("0x");
        for (byte b : bytes) {
            result.append(String.format("%02x", b));
        }
        return result.toString();
    }
}