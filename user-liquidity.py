import requests
import pandas as pd
import time

API_KEY = ""  # Replace with your API key
USDCE_ADDRESS = "0x29219dd400f2Bf60E5a23d13Be72B486D4038894"  # USDC.e token
WS_ADDRESS = "0x039e2fB66102314Ce7b64Ce5Ce3E5183bc94aD38"  # wS token
POOL_ADDRESS = "0x324963c267C354c7660Ce8CA3F5f167E05649970"  # Pool address
BASE_URL = "https://api.sonicscan.org/api"
OFFSET = 100 

START_BLOCK = 0
END_BLOCK = 15000000
BLOCK_STEP = 100000

# Prompt user for the recipient address to filter
user_address = input("Enter the recipient address to filter transactions: ").strip().lower()

current_start = START_BLOCK

# Function to fetch transactions for a given token
def fetch_transactions(token_address, wallet_address):
    all_transactions = []
    current_start = START_BLOCK

    while current_start <= END_BLOCK:
        current_end = min(current_start + BLOCK_STEP, END_BLOCK)
        page = 1

        while True:
            params = {
                "module": "account",
                "action": "tokentx",
                "contractaddress": token_address,
                "address": wallet_address,
                "page": page,
                "offset": OFFSET,
                "startblock": current_start,
                "endblock": current_end,
                "sort": "asc",
                "apikey": API_KEY
            }
            headers = {"User-Agent": "Mozilla/5.0"}

            try:
                response = requests.get(BASE_URL, params=params, headers=headers).json()

                if "status" in response and response["status"] == "0":
                    if "Max calls per sec rate limit reached" in response.get("message", ""):
                        print("Rate limit reached. Sleeping for 10 seconds...")
                        time.sleep(10)
                        continue

                if "result" in response and response["result"]:
                    valid_transactions = [tx for tx in response["result"] if isinstance(tx, dict)]
                    if valid_transactions:
                        print(f"Fetched {len(valid_transactions)} transactions...")
                        all_transactions.extend(valid_transactions)
                    else:
                        print("No valid transactions found on this page.")
                    page += 1
                else:
                    break

                time.sleep(5)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                time.sleep(10)
                continue

        current_start += BLOCK_STEP

    return all_transactions


# FETCH LIQUIDITY TRANSACTIONS
ws_transactions = fetch_transactions(WS_ADDRESS, user_address)
usdce_transactions = fetch_transactions(USDCE_ADDRESS, user_address)

liquidity_transactions = ws_transactions + usdce_transactions

# Convert to DataFrame
df_liquidity = pd.DataFrame(liquidity_transactions)

df_liquidity["value"] = df_liquidity["value"].astype(float)
df_liquidity["value"] = df_liquidity.apply(
    lambda row: row["value"] * 10**-18 if row["tokenSymbol"] == "wS" else row["value"] * 10**-6, axis=1
)


# Filter for transactions where POOL_ADDRESS is either 'from' or 'to'
df_liquidity_filtered = df_liquidity[(df_liquidity["from"].str.lower() == POOL_ADDRESS.lower()) | (df_liquidity["to"].str.lower() == POOL_ADDRESS.lower())]

output_file = f"liquidity_{user_address}.csv"
df_liquidity_filtered.to_csv(output_file, index=False)

print(f"Filtered transactions saved to {output_file}")

# Calculate total transfers for both tokens separately
ws_transfers = df_liquidity_filtered[df_liquidity_filtered["tokenSymbol"] == "wS"].apply(
    lambda row: -row["value"] if row["from"].lower() == POOL_ADDRESS.lower() and row["to"].lower() == user_address.lower()
    else row["value"] if row["from"].lower() == user_address.lower() and row["to"].lower() == POOL_ADDRESS.lower()
    else 0,
    axis=1
).sum()

usdce_transfers = df_liquidity_filtered[df_liquidity_filtered["tokenSymbol"] == "USDC.e"].apply(
    lambda row: -row["value"] if row["from"].lower() == POOL_ADDRESS.lower() and row["to"].lower() == user_address.lower()
    else row["value"] if row["from"].lower() == user_address.lower() and row["to"].lower() == POOL_ADDRESS.lower()
    else 0,
    axis=1
).sum()

print(f"Total wS added liquidity: {ws_transfers:.6f}")
print(f"Total USDC.e added liquidity: {usdce_transfers:.6f}")
