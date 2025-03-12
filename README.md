# Top profiters, rebalance frequency, and APR
This repo will calculate top profiting wallets, their rebalance frequency, and APR for wS-USDC.e pool on Shadow exchange. If analyzing for other pools, you can just adjust the addresses and token parameters.

## Fetching Transactions and Obtaining Top Wallets from Sonicscan

Sonicscan imposes limits on transaction retrieval:  
- **Sonicscan Website**: 5,000 transactions  
- **Sonicscan API**: 10,000 transactions  

To bypass these limitations, the following code fetches transactions in adjusted block increments.

### 1. `fetch-transactions.py`
- **Setup:**
  - Add your **Sonicscan API key**.
  - Edit the **contract address** (ERC-20 token).
  - Edit the **sender address** (rewards gauge).  

- **Additional Resources:**  
  - A list of gauge addresses for pools can be found under the ["Shadow Exchange - Revenue"](https://dune.com/shadow_exchange/main) query.  

- **Process:**  
  - Reward values in JSON are converted from **Wei to Ether**.  
  - Transactions are saved to a `.csv` file upon execution.

## Fetching Rebalance Frequecny and APR from a wallet address

### 1. `user-rewards.py`
Add your sonicscan API key to `API_KEY`. Run `python3 user-rewards.py` and input wallet you want to analyze for in user prompt. This will output a csv file of all transactions of incentives distribution with the filename `"rewards_{user_address}.csv"` as well as an output of incentives recieved.

### 2. `user-liquidity.py`
Add your sonicscan API key to `API_KEY`. Run `python3 user-liquidity.py` and input wallet you want to analyze for in user prompt. This will output a csv file of all liquidity transactions with the filename `"liquidity_{user_address}.csv"` as well as an output of net liquidity provided.

### 3. `rebalance_apr.py`
Add your coingecko "DEMO" API key to `"x-cg-demo-api-key"` (if PRO key, change header and endpoint accordingly.) Input wallet address to analyze for and the stats output from the past 2 programs (`user-rewards.py` and `user-liquidity.py`). This will output stats like this:
```
=== Rebalance Frequency Statistics ===
Total Rebalance Events: 20
Average Interval: 452763.75 seconds (~125.77 hours)
Median Interval: 341686.50 seconds (~94.91 hours)
Minimum Interval: 93.00 seconds
Maximum Interval: 1124685.00 seconds (~312.41 hours)
Rebalance Frequency per Day: 1.12 rebalances/day

=== Liquidity & APR Calculation ===
Total Added Liquidity (USD): $274863.72
Total Rewards Earned (USD): $23765.58
Liquidity Duration: 27.54 days
APR: 114.61%
```


