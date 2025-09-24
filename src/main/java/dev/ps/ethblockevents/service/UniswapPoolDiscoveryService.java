package dev.ps.ethblockevents.service;

import com.google.common.eventbus.EventBus;
import dev.ps.ethblockevents.config.EthereumProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Service;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.DefaultBlockParameter;
import org.web3j.protocol.core.methods.request.EthFilter;
import org.web3j.protocol.core.methods.response.Log;

import jakarta.annotation.PostConstruct;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

@Service
@ConfigurationProperties(prefix = "uniswap")
public class UniswapPoolDiscoveryService {
    
    private static final Logger logger = LoggerFactory.getLogger(UniswapPoolDiscoveryService.class);
    private static final String FACTORY_ADDRESS = "0x1F98431c8aD98523631AE4a59f267346ea31F984";
    private static final String POOL_CREATED_SIGNATURE = "0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118";
    
    private final Web3j web3j;
    private final EventBus eventBus;
    private final EthereumEventListenerService eventListener;
    private final Set<String> discoveredPools = ConcurrentHashMap.newKeySet();
    
    private List<PoolConfig> pools;
    
    public UniswapPoolDiscoveryService(Web3j web3j, EventBus eventBus, EthereumEventListenerService eventListener) {
        this.web3j = web3j;
        this.eventBus = eventBus;
        this.eventListener = eventListener;
    }
    
    @PostConstruct
    public void initialize() {
        // Add configured pools
        if (pools != null) {
            for (PoolConfig pool : pools) {
                addPoolToMonitoring(pool.getAddress(), pool.getName());
            }
        }
        
        // Listen for new pool creation events
        listenForNewPools();
    }
    
    private void addPoolToMonitoring(String poolAddress, String poolName) {
        if (discoveredPools.add(poolAddress)) {
            logger.info("Adding Uniswap pool to monitoring: {} ({})", poolName, poolAddress);
            
            // Create dynamic contract config for this pool
            EthereumProperties.ContractConfig poolContract = new EthereumProperties.ContractConfig(
                "UniswapV3Pool_" + poolName,
                poolAddress,
                List.of(new EthereumProperties.EventConfig(
                    "Swap",
                    "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67",
                    List.of(),
                    true
                )),
                null // no block range
            );
            
            // Add to event listener
            eventListener.addDynamicContract(poolContract);
        }
    }
    
    private void listenForNewPools() {
        try {
            EthFilter filter = new EthFilter(
                DefaultBlockParameter.valueOf("latest"),
                DefaultBlockParameter.valueOf("latest"),
                FACTORY_ADDRESS
            );
            filter.addSingleTopic(POOL_CREATED_SIGNATURE);
            
            web3j.ethLogFlowable(filter).subscribe(
                this::handlePoolCreated,
                error -> logger.error("Error listening for new pools: {}", error.getMessage())
            );
            
            logger.info("Started listening for new Uniswap pool creation events");
            
        } catch (Exception e) {
            logger.error("Failed to start pool discovery: {}", e.getMessage(), e);
        }
    }
    
    private void handlePoolCreated(Log log) {
        try {
            if (log.getTopics().size() >= 4) {
                String token0 = "0x" + log.getTopics().get(1).substring(26);
                String token1 = "0x" + log.getTopics().get(2).substring(26);
                String poolAddress = "0x" + log.getData().substring(26, 66);
                
                String poolName = String.format("%s/%s", 
                    token0.substring(0, 6), token1.substring(0, 6));
                
                logger.info("New Uniswap pool created: {} at {}", poolName, poolAddress);
                addPoolToMonitoring(poolAddress, poolName);
            }
        } catch (Exception e) {
            logger.error("Error processing pool creation event: {}", e.getMessage(), e);
        }
    }
    
    public List<PoolConfig> getPools() {
        return pools;
    }
    
    public void setPools(List<PoolConfig> pools) {
        this.pools = pools;
    }
    
    public static class PoolConfig {
        private String address;
        private String name;
        private String token0;
        private String token1;
        private int fee;
        
        public String getAddress() { return address; }
        public void setAddress(String address) { this.address = address; }
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getToken0() { return token0; }
        public void setToken0(String token0) { this.token0 = token0; }
        
        public String getToken1() { return token1; }
        public void setToken1(String token1) { this.token1 = token1; }
        
        public int getFee() { return fee; }
        public void setFee(int fee) { this.fee = fee; }
    }
}