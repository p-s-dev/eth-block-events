package dev.ps.ethblockevents.config;

import com.google.common.eventbus.EventBus;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.http.HttpService;
import org.web3j.protocol.websocket.WebSocketService;

@Configuration
public class ApplicationConfig {

    @Bean
    public EventBus eventBus() {
        return new EventBus("EthereumEventBus");
    }

    @Bean
    public Web3j web3j(EthereumProperties ethereumProperties) {
        return Web3j.build(new HttpService(ethereumProperties.nodeUrl()));
    }

    @Bean
    public Web3j web3jWebsocket(EthereumProperties ethereumProperties) {
        if (ethereumProperties.websocketUrl() != null && 
            !ethereumProperties.websocketUrl().trim().isEmpty()) {
            try {
                WebSocketService webSocketService = new WebSocketService(ethereumProperties.websocketUrl(), false);
                return Web3j.build(webSocketService);
            } catch (Exception e) {
                // If WebSocket fails, fall back to HTTP
                return Web3j.build(new HttpService(ethereumProperties.nodeUrl()));
            }
        }
        // Fallback to HTTP service if WebSocket URL is not provided
        return Web3j.build(new HttpService(ethereumProperties.nodeUrl()));
    }
}