package dev.ps.ethblockevents.config;

import com.google.common.eventbus.EventBus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.http.HttpService;
import org.web3j.protocol.websocket.WebSocketService;

@Configuration
public class ApplicationConfig {

    private static final Logger logger = LoggerFactory.getLogger(ApplicationConfig.class);

    @Bean
    public EventBus eventBus() {
        return new EventBus("EthereumEventBus");
    }

    @Bean
    public Web3j web3j(EthereumProperties ethereumProperties) {
        logger.info("Connecting to Ethereum node via HTTP: {}", ethereumProperties.nodeUrl());
        return Web3j.build(new HttpService(ethereumProperties.nodeUrl()));
    }

    @Bean
    public Web3j web3jWebsocket(EthereumProperties ethereumProperties) {
        if (ethereumProperties.websocketUrl() != null && 
            !ethereumProperties.websocketUrl().trim().isEmpty()) {
            try {
                logger.info("Connecting to Ethereum node via WebSocket: {}", ethereumProperties.websocketUrl());
                WebSocketService webSocketService = new WebSocketService(ethereumProperties.websocketUrl(), false);
                webSocketService.connect();
                return Web3j.build(webSocketService);
            } catch (Exception e) {
                logger.warn("WebSocket connection failed, falling back to HTTP: {}", ethereumProperties.nodeUrl());
                return Web3j.build(new HttpService(ethereumProperties.nodeUrl()));
            }
        }
        logger.info("No WebSocket URL configured, using HTTP: {}", ethereumProperties.nodeUrl());
        return Web3j.build(new HttpService(ethereumProperties.nodeUrl()));
    }
}