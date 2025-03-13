# Top profiters, rebalance frequency, and APR
This repo will calculate top profiting wallets, their rebalance frequency, and APR for wS-USDC.e pool on Shadow exchange. If analyzing for other pools, you can just adjust the addresses and token parameters.

## Fetching Transactions and Obtaining Top Wallets from Sonicscan

Sonicscan imposes limits on transaction retrieval:  
- **Sonicscan Website**: 5,000 transactions  
- **Sonicscan API**: 10,000 transactions  

To bypass these limitations, the following code fetches transactions in adjusted block increments.

### `top-wallets.py`
- **Setup:**
  - Add your **Sonicscan API key**.
  - If you want to use a different pool:
    - Edit the **contract address** (ERC-20 token).
    - Edit the **sender address** (rewards gauge).  

- **Additional Resources:**  
  - A list of gauge addresses for pools can be found under the ["Shadow Exchange - Revenue"](https://dune.com/shadow_exchange/main) query.  

- **Process:**  
  - Reward values in JSON are converted from **Wei to Ether**.  
  - Transactions are saved to a `.csv` file upon execution.

## Fetching Individual Wallet Stats (Rebalance, APR, transactions, etc)
### `user-stats.py`
- **Setup:**
  - Add your API keys to `SONICSCAN_API_KEY` and `COINGECKO_API_KEY` (this is setup for coingecko demo API key. If PRO key, adjust accordingly.)
  - Edit the addresses if you want to look at other pools or tokens.

- Output:
  1. `rewards_{wallet_address}.csv`
    This will list all the transactions of rewards distributed to the pertaining wallet address.
  2. `liquidity_{wallet_address}.csv`
    This will list all the transactions of the pertaining wallet address' increase/decrease liquidity to the pool.
  3. `stats_{wallet_address}.txt`
    This will list all the stats (amount of net liquidity provided, rewards recieved, rebalance frequency, and APR) of the pertaining wallet.
    Sample output:
    ```
    Total wS added liquidity: 592996.803577
    Total USDC.e added liquidity: 26918.002937
    Total $SHADOW tokens received: 0.014721
    Total $xSHADOW tokens received: 382.891756
    
    === Rebalance Frequency Statistics ===
    Total Rebalance Events: 20
    Average Interval: 452763.75 seconds (~125.77 hours)
    Median Interval: 341686.50 seconds (~94.91 hours)
    Minimum Interval: 93.00 seconds
    Maximum Interval: 1124685.00 seconds (~312.41 hours)
    Rebalance Frequency per Day: 1.12 rebalances/day
    
    === Liquidity & APR Calculation ===
    Total Added Liquidity (USD): $294728.05
    Total Rewards Earned (USD): $28231.69
    Liquidity Duration: 28.67 days
    APR: 121.93%
  ```

## In-progress:
 - clean code
