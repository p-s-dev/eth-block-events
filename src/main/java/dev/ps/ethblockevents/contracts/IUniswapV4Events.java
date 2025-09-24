package dev.ps.ethblockevents.contracts;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.web3j.abi.TypeReference;
import org.web3j.abi.datatypes.Address;
import org.web3j.abi.datatypes.Event;
import org.web3j.abi.datatypes.generated.Bytes32;
import org.web3j.abi.datatypes.generated.Int128;
import org.web3j.abi.datatypes.generated.Int24;
import org.web3j.abi.datatypes.generated.Int256;
import org.web3j.abi.datatypes.generated.Uint128;
import org.web3j.abi.datatypes.generated.Uint160;
import org.web3j.abi.datatypes.generated.Uint24;
import org.web3j.crypto.Credentials;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.methods.response.BaseEventResponse;
import org.web3j.protocol.core.methods.response.TransactionReceipt;
import org.web3j.tx.Contract;
import org.web3j.tx.TransactionManager;
import org.web3j.tx.gas.ContractGasProvider;

/**
 * <p>Auto generated code.
 * <p><strong>Do not modify!</strong>
 * <p>Please use the <a href="https://docs.web3j.io/command_line.html">web3j command line tools</a>,
 * or the org.web3j.codegen.SolidityFunctionWrapperGenerator in the 
 * <a href="https://github.com/web3j/web3j/tree/master/codegen">codegen module</a> to update.
 *
 * <p>Generated with web3j version 4.10.3.
 */
@SuppressWarnings("rawtypes")
public class IUniswapV4Events extends Contract {
    public static final String BINARY = "";

    public static final Event INITIALIZE_EVENT = new Event("Initialize",
            Arrays.<TypeReference<?>>asList(
                    new TypeReference<Bytes32>(true) {},
                    new TypeReference<Address>(true) {},
                    new TypeReference<Address>(true) {},
                    new TypeReference<Uint24>() {},
                    new TypeReference<Int24>() {},
                    new TypeReference<Address>() {}
            ));

    public static final Event MODIFY_LIQUIDITY_EVENT = new Event("ModifyLiquidity",
            Arrays.<TypeReference<?>>asList(
                    new TypeReference<Bytes32>(true) {},
                    new TypeReference<Address>(true) {},
                    new TypeReference<Int24>() {},
                    new TypeReference<Int24>() {},
                    new TypeReference<Int256>() {}
            ));

    public static final Event SWAP_EVENT = new Event("Swap",
            Arrays.<TypeReference<?>>asList(
                    new TypeReference<Bytes32>(true) {},
                    new TypeReference<Address>(true) {},
                    new TypeReference<Int128>() {},
                    new TypeReference<Int128>() {},
                    new TypeReference<Uint160>() {},
                    new TypeReference<Uint128>() {},
                    new TypeReference<Int24>() {}
            ));

    @Deprecated
    protected IUniswapV4Events(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    protected IUniswapV4Events(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        super(BINARY, contractAddress, web3j, credentials, contractGasProvider);
    }

    @Deprecated
    protected IUniswapV4Events(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    protected IUniswapV4Events(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        super(BINARY, contractAddress, web3j, transactionManager, contractGasProvider);
    }

    public static List<InitializeEventResponse> getInitializeEvents(TransactionReceipt transactionReceipt) {
        List<Contract.EventValuesWithLog> valueList = staticExtractEventParametersWithLog(INITIALIZE_EVENT, transactionReceipt);
        ArrayList<InitializeEventResponse> responses = new ArrayList<InitializeEventResponse>(valueList.size());
        for (Contract.EventValuesWithLog eventValues : valueList) {
            InitializeEventResponse typedResponse = new InitializeEventResponse();
            typedResponse.log = eventValues.getLog();
            typedResponse.poolId = (byte[]) eventValues.getIndexedValues().get(0).getValue();
            typedResponse.currency0 = (String) eventValues.getIndexedValues().get(1).getValue();
            typedResponse.currency1 = (String) eventValues.getIndexedValues().get(2).getValue();
            typedResponse.fee = (BigInteger) eventValues.getNonIndexedValues().get(0).getValue();
            typedResponse.tickSpacing = (BigInteger) eventValues.getNonIndexedValues().get(1).getValue();
            typedResponse.hooks = (String) eventValues.getNonIndexedValues().get(2).getValue();
            responses.add(typedResponse);
        }
        return responses;
    }

    public static List<ModifyLiquidityEventResponse> getModifyLiquidityEvents(TransactionReceipt transactionReceipt) {
        List<Contract.EventValuesWithLog> valueList = staticExtractEventParametersWithLog(MODIFY_LIQUIDITY_EVENT, transactionReceipt);
        ArrayList<ModifyLiquidityEventResponse> responses = new ArrayList<ModifyLiquidityEventResponse>(valueList.size());
        for (Contract.EventValuesWithLog eventValues : valueList) {
            ModifyLiquidityEventResponse typedResponse = new ModifyLiquidityEventResponse();
            typedResponse.log = eventValues.getLog();
            typedResponse.poolId = (byte[]) eventValues.getIndexedValues().get(0).getValue();
            typedResponse.sender = (String) eventValues.getIndexedValues().get(1).getValue();
            typedResponse.tickLower = (BigInteger) eventValues.getNonIndexedValues().get(0).getValue();
            typedResponse.tickUpper = (BigInteger) eventValues.getNonIndexedValues().get(1).getValue();
            typedResponse.liquidityDelta = (BigInteger) eventValues.getNonIndexedValues().get(2).getValue();
            responses.add(typedResponse);
        }
        return responses;
    }

    public static List<SwapEventResponse> getSwapEvents(TransactionReceipt transactionReceipt) {
        List<Contract.EventValuesWithLog> valueList = staticExtractEventParametersWithLog(SWAP_EVENT, transactionReceipt);
        ArrayList<SwapEventResponse> responses = new ArrayList<SwapEventResponse>(valueList.size());
        for (Contract.EventValuesWithLog eventValues : valueList) {
            SwapEventResponse typedResponse = new SwapEventResponse();
            typedResponse.log = eventValues.getLog();
            typedResponse.poolId = (byte[]) eventValues.getIndexedValues().get(0).getValue();
            typedResponse.sender = (String) eventValues.getIndexedValues().get(1).getValue();
            typedResponse.amount0 = (BigInteger) eventValues.getNonIndexedValues().get(0).getValue();
            typedResponse.amount1 = (BigInteger) eventValues.getNonIndexedValues().get(1).getValue();
            typedResponse.sqrtPriceX96 = (BigInteger) eventValues.getNonIndexedValues().get(2).getValue();
            typedResponse.liquidity = (BigInteger) eventValues.getNonIndexedValues().get(3).getValue();
            typedResponse.tick = (BigInteger) eventValues.getNonIndexedValues().get(4).getValue();
            responses.add(typedResponse);
        }
        return responses;
    }

    @Deprecated
    public static IUniswapV4Events load(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        return new IUniswapV4Events(contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    @Deprecated
    public static IUniswapV4Events load(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        return new IUniswapV4Events(contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    public static IUniswapV4Events load(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        return new IUniswapV4Events(contractAddress, web3j, credentials, contractGasProvider);
    }

    public static IUniswapV4Events load(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        return new IUniswapV4Events(contractAddress, web3j, transactionManager, contractGasProvider);
    }

    public static class InitializeEventResponse extends BaseEventResponse {
        public byte[] poolId;
        public String currency0;
        public String currency1;
        public BigInteger fee;
        public BigInteger tickSpacing;
        public String hooks;
    }

    public static class ModifyLiquidityEventResponse extends BaseEventResponse {
        public byte[] poolId;
        public String sender;
        public BigInteger tickLower;
        public BigInteger tickUpper;
        public BigInteger liquidityDelta;
    }

    public static class SwapEventResponse extends BaseEventResponse {
        public byte[] poolId;
        public String sender;
        public BigInteger amount0;
        public BigInteger amount1;
        public BigInteger sqrtPriceX96;
        public BigInteger liquidity;
        public BigInteger tick;
    }
}