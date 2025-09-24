package dev.ps.ethblockevents.service;

import com.google.common.eventbus.EventBus;
import dev.ps.ethblockevents.config.EthereumProperties;
import dev.ps.ethblockevents.model.BlockEvent;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.methods.response.EthBlock;

import java.math.BigInteger;
import java.time.Instant;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.mockito.Mockito.*;

class EthereumEventListenerServiceTest {

    @Mock
    private Web3j web3j;
    
    @Mock
    private Web3j web3jWebsocket;
    
    @Mock
    private EventBus eventBus;
    
    @Mock
    private EthereumProperties ethereumProperties;
    
    @Mock
    private GenericContractEventListener mockEventListener;

    private EthereumEventListenerService service;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        List<GenericContractEventListener> eventListeners = Collections.singletonList(mockEventListener);
        service = new EthereumEventListenerService(web3j, web3jWebsocket, eventBus, ethereumProperties, eventListeners);
    }

    @Test
    void testStartBlockListening_skipWhenWebSocketUrlEmpty() {
        // Given
        when(ethereumProperties.websocketUrl()).thenReturn("");
        
        // When
        service.startBlockListening();
        
        // Then
        verifyNoInteractions(web3jWebsocket);
    }

    @Test
    void testStartBlockListening_skipWhenWebSocketUrlNull() {
        // Given
        when(ethereumProperties.websocketUrl()).thenReturn(null);
        
        // When
        service.startBlockListening();
        
        // Then
        verifyNoInteractions(web3jWebsocket);
    }

    @Test
    void testHandleBlockEvent() {
        // Given
        EthBlock.Block block = mock(EthBlock.Block.class);
        EthBlock ethBlock = mock(EthBlock.class);
        when(ethBlock.getBlock()).thenReturn(block);
        
        when(block.getNumber()).thenReturn(BigInteger.valueOf(12345));
        when(block.getHash()).thenReturn("0xblockhash");
        when(block.getParentHash()).thenReturn("0xparenthash");
        when(block.getGasLimit()).thenReturn(BigInteger.valueOf(30000000));
        when(block.getGasUsed()).thenReturn(BigInteger.valueOf(15000000));
        when(block.getTimestamp()).thenReturn(BigInteger.valueOf(1640995200));
        when(block.getMiner()).thenReturn("0xminer");
        when(block.getTransactions()).thenReturn(Collections.emptyList());
        
        // When
        service.handleBlockEvent(ethBlock);
        
        // Then
        verify(eventBus).post(any(BlockEvent.class));
    }
}