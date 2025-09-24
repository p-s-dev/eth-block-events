package dev.ps.ethblockevents.service;

import com.google.common.eventbus.EventBus;
import dev.ps.ethblockevents.config.EthereumProperties;
import dev.ps.ethblockevents.model.UniswapInitializeEvent;
import dev.ps.ethblockevents.model.UniswapModifyLiquidityEvent;
import dev.ps.ethblockevents.model.UniswapSwapEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.DefaultBlockParameter;
import org.web3j.protocol.core.methods.response.EthBlock;
import org.web3j.protocol.core.methods.response.Log;

import java.math.BigInteger;
import java.time.Instant;
import java.util.List;

/**
 * Specialized event listener for Uniswap V4 contract events
 */
@Component
public class UniswapEventListener implements GenericContractEventListener {
    
    private static final Logger logger = LoggerFactory.getLogger(UniswapEventListener.class);
    
    private final EventBus eventBus;
    private final Web3j web3j;
    
    public UniswapEventListener(EventBus eventBus, Web3j web3j) {
        this.eventBus = eventBus;
        this.web3j = web3j;
    }
    
    @Override
    public boolean handleEvent(Log log, EthereumProperties.ContractConfig contractConfig, 
                              EthereumProperties.EventConfig eventConfig) {
        
        if (!supportsContract(contractConfig)) {
            return false;
        }
        
        try {
            String eventSignature = log.getTopics().get(0);
            Instant timestamp = getBlockTimestamp(log.getBlockNumber());
            
            switch (eventSignature) {
                case UniswapSwapEvent.TOPIC_0:
                    handleSwapEvent(log, timestamp);
                    return true;
                    
                case UniswapInitializeEvent.TOPIC_0:
                    handleInitializeEvent(log, timestamp);
                    return true;
                    
                case UniswapModifyLiquidityEvent.TOPIC_0:
                    handleModifyLiquidityEvent(log, timestamp);
                    return true;
                    
                default:
                    logger.debug("Unknown Uniswap event signature: {}", eventSignature);
                    return false;
            }
            
        } catch (Exception e) {
            logger.error("Error handling Uniswap event: {}", e.getMessage(), e);
            return false;
        }
    }
    
    @Override
    public boolean supportsContract(EthereumProperties.ContractConfig contractConfig) {
        // Check if this is a Uniswap contract (could be improved with better identification)
        return contractConfig.name() != null && 
               (contractConfig.name().toLowerCase().contains("uniswap") ||
                contractConfig.events().stream().anyMatch(event -> 
                    UniswapSwapEvent.TOPIC_0.equals(event.signature()) ||
                    UniswapInitializeEvent.TOPIC_0.equals(event.signature()) ||
                    UniswapModifyLiquidityEvent.TOPIC_0.equals(event.signature())
                ));
    }
    
    @Override
    public int getPriority() {
        return 10; // Higher priority for specialized handlers
    }
    
    private void handleSwapEvent(Log log, Instant timestamp) {
        try {
            if (log.getTopics().size() < 3) {
                logger.warn("Invalid Uniswap Swap event - not enough topics");
                return;
            }
            
            // Extract indexed parameters
            byte[] poolId = hexStringToByteArray(log.getTopics().get(1));
            String sender = "0x" + log.getTopics().get(2).substring(26);
            
            // For now, create event with basic data and null for complex decoded fields
            // TODO: Implement proper ABI decoding
            UniswapSwapEvent swapEvent = new UniswapSwapEvent(
                log.getAddress(),
                poolId,
                sender,
                BigInteger.ZERO, // amount0 - TODO: decode from data
                BigInteger.ZERO, // amount1 - TODO: decode from data  
                BigInteger.ZERO, // sqrtPriceX96 - TODO: decode from data
                BigInteger.ZERO, // liquidity - TODO: decode from data
                BigInteger.ZERO, // tick - TODO: decode from data
                log.getTransactionHash(),
                log.getBlockNumber(),
                log.getLogIndex(),
                timestamp
            );
            
            eventBus.post(swapEvent);
            logger.info("Published Uniswap Swap event for pool: {} by sender: {} (detailed decoding pending)", 
                       bytesToHex(poolId), sender);
            
        } catch (Exception e) {
            logger.error("Error handling Uniswap Swap event: {}", e.getMessage(), e);
        }
    }
    
    private void handleInitializeEvent(Log log, Instant timestamp) {
        try {
            if (log.getTopics().size() < 4) {
                logger.warn("Invalid Uniswap Initialize event - not enough topics");
                return;
            }
            
            // Extract indexed parameters
            byte[] poolId = hexStringToByteArray(log.getTopics().get(1));
            String currency0 = "0x" + log.getTopics().get(2).substring(26);
            String currency1 = "0x" + log.getTopics().get(3).substring(26);
            
            // For now, create event with basic data and defaults for complex decoded fields
            // TODO: Implement proper ABI decoding
            UniswapInitializeEvent initEvent = new UniswapInitializeEvent(
                log.getAddress(),
                poolId,
                currency0,
                currency1,
                BigInteger.ZERO, // fee - TODO: decode from data
                BigInteger.ZERO, // tickSpacing - TODO: decode from data
                "0x0000000000000000000000000000000000000000", // hooks - TODO: decode from data
                log.getTransactionHash(),
                log.getBlockNumber(),
                log.getLogIndex(),
                timestamp
            );
            
            eventBus.post(initEvent);
            logger.info("Published Uniswap Initialize event for pool: {} with currencies: {} <-> {} (detailed decoding pending)", 
                       bytesToHex(poolId), currency0, currency1);
            
        } catch (Exception e) {
            logger.error("Error handling Uniswap Initialize event: {}", e.getMessage(), e);
        }
    }
    
    private void handleModifyLiquidityEvent(Log log, Instant timestamp) {
        try {
            if (log.getTopics().size() < 3) {
                logger.warn("Invalid Uniswap ModifyLiquidity event - not enough topics");
                return;
            }
            
            // Extract indexed parameters
            byte[] poolId = hexStringToByteArray(log.getTopics().get(1));
            String sender = "0x" + log.getTopics().get(2).substring(26);
            
            // For now, create event with basic data and defaults for complex decoded fields
            // TODO: Implement proper ABI decoding
            UniswapModifyLiquidityEvent modifyEvent = new UniswapModifyLiquidityEvent(
                log.getAddress(),
                poolId,
                sender,
                BigInteger.ZERO, // tickLower - TODO: decode from data
                BigInteger.ZERO, // tickUpper - TODO: decode from data
                BigInteger.ZERO, // liquidityDelta - TODO: decode from data
                log.getTransactionHash(),
                log.getBlockNumber(),
                log.getLogIndex(),
                timestamp
            );
            
            eventBus.post(modifyEvent);
            logger.info("Published Uniswap ModifyLiquidity event for pool: {} by sender: {} (detailed decoding pending)", 
                       bytesToHex(poolId), sender);
            
        } catch (Exception e) {
            logger.error("Error handling Uniswap ModifyLiquidity event: {}", e.getMessage(), e);
        }
    }
    
    private Instant getBlockTimestamp(BigInteger blockNumber) {
        try {
            EthBlock ethBlock = web3j.ethGetBlockByNumber(
                DefaultBlockParameter.valueOf(blockNumber), false
            ).send();
            
            if (ethBlock.getBlock() != null) {
                return Instant.ofEpochSecond(ethBlock.getBlock().getTimestamp().longValue());
            }
        } catch (Exception e) {
            logger.warn("Failed to get block timestamp for block {}: {}", blockNumber, e.getMessage());
        }
        return Instant.now();
    }
    
    private byte[] hexStringToByteArray(String hex) {
        // Remove 0x prefix if present
        hex = hex.startsWith("0x") ? hex.substring(2) : hex;
        
        int len = hex.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(hex.charAt(i), 16) << 4)
                                 + Character.digit(hex.charAt(i+1), 16));
        }
        return data;
    }
    
    private String bytesToHex(byte[] bytes) {
        StringBuilder result = new StringBuilder("0x");
        for (byte b : bytes) {
            result.append(String.format("%02x", b));
        }
        return result.toString();
    }
}