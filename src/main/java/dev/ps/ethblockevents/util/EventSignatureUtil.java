package dev.ps.ethblockevents.util;

import org.web3j.crypto.Hash;

/**
 * Utility class for generating Ethereum event signatures
 */
public class EventSignatureUtil {

    /**
     * Generate the Keccak256 hash of an event signature
     * 
     * @param eventSignature The event signature in format: "EventName(type1,type2,...)"
     * @return The hex string of the Keccak256 hash with 0x prefix
     */
    public static String generateEventSignature(String eventSignature) {
        // Use Web3j's Keccak256 implementation
        return Hash.sha3String(eventSignature);
    }

    /**
     * Common Ethereum event signatures
     */
    public static class CommonSignatures {
        public static final String ERC20_TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";
        public static final String ERC20_APPROVAL = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925";
        public static final String ERC721_TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";
        public static final String ERC721_APPROVAL = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925";
        public static final String ERC721_APPROVAL_FOR_ALL = "0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31";
        
        // Uniswap V4 event signatures
        public static final String UNISWAP_SWAP = generateEventSignature("Swap(bytes32,address,int128,int128,uint160,uint128,int24)");
        public static final String UNISWAP_INITIALIZE = generateEventSignature("Initialize(bytes32,address,address,uint24,int24,address)");
        public static final String UNISWAP_MODIFY_LIQUIDITY = generateEventSignature("ModifyLiquidity(bytes32,address,int24,int24,int256)");
    }

    public static void main(String[] args) {
        // Example usage - generates correct event signatures
        System.out.println("ERC20 Transfer: " + generateEventSignature("Transfer(address,address,uint256)"));
        System.out.println("ERC20 Approval: " + generateEventSignature("Approval(address,address,uint256)"));
        System.out.println("Uniswap Swap: " + generateEventSignature("Swap(bytes32,address,int128,int128,uint160,uint128,int24)"));
        System.out.println("Uniswap Initialize: " + generateEventSignature("Initialize(bytes32,address,address,uint24,int24,address)"));
        System.out.println("Uniswap ModifyLiquidity: " + generateEventSignature("ModifyLiquidity(bytes32,address,int24,int24,int256)"));
    }
}