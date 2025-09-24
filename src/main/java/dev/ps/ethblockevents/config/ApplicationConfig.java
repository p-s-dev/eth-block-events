package dev.ps.ethblockevents.config;

import com.google.common.eventbus.EventBus;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.http.HttpService;

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
}