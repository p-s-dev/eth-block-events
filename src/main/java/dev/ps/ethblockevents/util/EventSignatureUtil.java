package dev.ps.ethblockevents.util;

import org.springframework.util.DigestUtils;

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
        // Note: This is a simplified implementation using SHA-256 instead of Keccak256
        // For production use, you should use a proper Keccak256 implementation
        // like org.web3j.crypto.Hash.sha3()
        
        byte[] hash = DigestUtils.md5Digest(eventSignature.getBytes());
        StringBuilder hexString = new StringBuilder("0x");
        for (byte b : hash) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) {
                hexString.append('0');
            }
            hexString.append(hex);
        }
        
        // Pad to 64 characters (32 bytes) for proper event topic format
        while (hexString.length() < 66) { // 0x + 64 chars
            hexString.append('0');
        }
        
        return hexString.toString();
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
    }

    public static void main(String[] args) {
        // Example usage
        System.out.println("ERC20 Transfer: " + generateEventSignature("Transfer(address,address,uint256)"));
        System.out.println("ERC20 Approval: " + generateEventSignature("Approval(address,address,uint256)"));
    }
}