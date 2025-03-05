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

### 2. `analyze-transactions.py`
- Fetches the **top wallets** (default: **10**) based on the **sum of rewards** calculated from the `.csv` file.  


