package dev.ps.ethblockevents.service;

import com.google.common.eventbus.EventBus;
import dev.ps.ethblockevents.config.EthereumProperties;
import dev.ps.ethblockevents.model.UniswapSwapEvent;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.methods.response.Log;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.Collections;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class UniswapEventListenerTest {

    @Mock
    private EventBus eventBus;
    
    @Mock
    private Web3j web3j;
    
    @Mock
    private Log mockLog;

    private UniswapEventListener listener;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        listener = new UniswapEventListener(eventBus, web3j);
    }

    @Test
    void testSupportsUniswapContract() {
        // Given
        EthereumProperties.EventConfig swapEvent = new EthereumProperties.EventConfig(
            "Swap", 
            UniswapSwapEvent.TOPIC_0, 
            Collections.emptyList(), 
            true
        );
        EthereumProperties.ContractConfig uniswapConfig = new EthereumProperties.ContractConfig(
            "UniswapV4",
            "0x1234567890123456789012345678901234567890",
            Collections.singletonList(swapEvent),
            null
        );

        // When
        boolean supports = listener.supportsContract(uniswapConfig);

        // Then
        assertTrue(supports);
    }

    @Test
    void testDoesNotSupportNonUniswapContract() {
        // Given
        EthereumProperties.EventConfig transferEvent = new EthereumProperties.EventConfig(
            "Transfer", 
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef", 
            Collections.emptyList(), 
            true
        );
        EthereumProperties.ContractConfig erc20Config = new EthereumProperties.ContractConfig(
            "USDC",
            "0x1234567890123456789012345678901234567890",
            Collections.singletonList(transferEvent),
            null
        );

        // When
        boolean supports = listener.supportsContract(erc20Config);

        // Then
        assertFalse(supports);
    }

    @Test
    void testHandleSwapEvent() {
        // Given
        when(mockLog.getTopics()).thenReturn(Arrays.asList(
            UniswapSwapEvent.TOPIC_0,
            "0x1234567890123456789012345678901234567890123456789012345678901234", // poolId
            "0x0000000000000000000000001234567890123456789012345678901234567890"  // sender
        ));
        when(mockLog.getAddress()).thenReturn("0xUniswapContract");
        when(mockLog.getTransactionHash()).thenReturn("0xTxHash");
        when(mockLog.getBlockNumber()).thenReturn(BigInteger.valueOf(12345));
        when(mockLog.getLogIndex()).thenReturn(BigInteger.valueOf(1));
        when(mockLog.getData()).thenReturn("0x");

        EthereumProperties.EventConfig eventConfig = new EthereumProperties.EventConfig(
            "Swap", UniswapSwapEvent.TOPIC_0, Collections.emptyList(), true
        );
        EthereumProperties.ContractConfig contractConfig = new EthereumProperties.ContractConfig(
            "UniswapV4", "0xUniswapContract", Collections.singletonList(eventConfig), null
        );

        // When
        boolean handled = listener.handleEvent(mockLog, contractConfig, eventConfig);

        // Then
        assertTrue(handled);
        
        ArgumentCaptor<UniswapSwapEvent> eventCaptor = ArgumentCaptor.forClass(UniswapSwapEvent.class);
        verify(eventBus).post(eventCaptor.capture());
        
        UniswapSwapEvent capturedEvent = eventCaptor.getValue();
        assertEquals("0xUniswapContract", capturedEvent.contractAddress());
        assertEquals("0x1234567890123456789012345678901234567890", capturedEvent.sender());
    }

    @Test
    void testGetPriority() {
        // When
        int priority = listener.getPriority();

        // Then
        assertEquals(10, priority);
    }
}