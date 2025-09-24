// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Interface for Uniswap V4 events
interface IUniswapV4Events {
    /// @notice Emitted when a pool is initialized
    /// @param poolId The pool identifier
    /// @param currency0 The first currency of the pool by address sort order
    /// @param currency1 The second currency of the pool by address sort order
    /// @param fee The fee of the pool
    /// @param tickSpacing The tick spacing of the pool
    /// @param hooks The hooks contract address
    event Initialize(
        bytes32 indexed poolId,
        address indexed currency0,
        address indexed currency1,
        uint24 fee,
        int24 tickSpacing,
        address hooks
    );

    /// @notice Emitted for swaps between currency0 and currency1
    /// @param poolId The pool identifier
    /// @param sender The address that initiated the swap call
    /// @param amount0 The delta of the balance of currency0 of the pool, exact when negative, minimum when positive
    /// @param amount1 The delta of the balance of currency1 of the pool, exact when negative, minimum when positive
    /// @param sqrtPriceX96 The price of the pool after the swap
    /// @param liquidity The liquidity of the pool after the swap
    /// @param tick The log base 1.0001 of price of the pool after the swap
    event Swap(
        bytes32 indexed poolId,
        address indexed sender,
        int128 amount0,
        int128 amount1,
        uint160 sqrtPriceX96,
        uint128 liquidity,
        int24 tick
    );

    /// @notice Emitted when liquidity is modified to a pool
    /// @param poolId The pool identifier
    /// @param sender The address that modified the liquidity
    /// @param tickLower The lower tick of the position
    /// @param tickUpper The upper tick of the position
    /// @param liquidityDelta The amount of liquidity that was added or removed
    event ModifyLiquidity(
        bytes32 indexed poolId,
        address indexed sender,
        int24 tickLower,
        int24 tickUpper,
        int256 liquidityDelta
    );
}