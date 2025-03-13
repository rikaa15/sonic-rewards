import requests
import pandas as pd
import time
from datetime import datetime, timezone

API_KEY = ""  # Replace with your API key
USDCE_ADDRESS = "0x29219dd400f2Bf60E5a23d13Be72B486D4038894"  # USDC.e token
WS_ADDRESS = "0x039e2fB66102314Ce7b64Ce5Ce3E5183bc94aD38"  # wS token
POOL_ADDRESS = "0x324963c267C354c7660Ce8CA3F5f167E05649970"  # Pool address
SHADOW_ADDRESS = "0x3333b97138D4b086720b5aE8A7844b1345a33333"  # SHADOW token
XSHADOW_ADDRESS = "0x5050bc082FF4A74Fb6B0B04385dEfdDB114b2424"  # xSHADOW token
SENDER_ADDRESS = "0x0ac98Ce57D24f77F48161D12157cb815Af469fc0"  # Gauge address
BASE_URL = "https://api.sonicscan.org/api"
OFFSET = 100 

START_BLOCK = 0
END_BLOCK = 15000000
BLOCK_STEP = 100000

# Prompt user for the recipient address to filter
user_address = input("Enter the recipient address to filter transactions: ").strip().lower()
log_file = f"stats_{user_address}.txt"

def log_to_file(message):
    with open(log_file, "a") as f:
        f.write(message + "\n")

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


def fetch_token_prices():
    """Fetch latest prices of wS, USDC.e, SHADOW, and xSHADOW tokens"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": "CG-kZxN6wxBbKn6DhoU3fWkiWui"  # Your CoinGecko API Key
        }
        params = {
            "ids": "wrapped-sonic,sonic-bridged-usdc-e-sonic,shadow-2",  # Adjust token IDs here
            "vs_currencies": "usd"
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        print("Data received from CoinGecko API:", data)  # Print the raw response for debugging

        return {
            "wS_price": data.get("wrapped-sonic", {}).get("usd", 0),
            "USDC.e_price": data.get("sonic-bridged-usdc-e-sonic", {}).get("usd", 1),
            "SHADOW_price": data.get("shadow-2", {}).get("usd", 0),
            "xSHADOW_price": data.get("shadow-2", {}).get("usd", 0)  # xSHADOW = SHADOW price
        }
    except Exception as e:
        print(f"Error fetching token prices: {e}")
        return None

def calculate_rebalance_frequency_and_apr(user_address, ws_transfers, usdce_transfers, shadow_rewards, xshadow_rewards):
    # Construct the filename based on the address
    file_path = f"liquidity_{user_address}.csv"

    try:
        df = pd.read_csv(file_path)

        df["dateTime"] = pd.to_datetime(df["timeStamp"], unit="s")

        df = df.sort_values(by="dateTime")

        # Group transactions by blockHash (each unique blockHash represents a single rebalance event)
        df_grouped = df.groupby("blockHash")["dateTime"].first().reset_index()

        # Calculate time differences between consecutive rebalance events
        df_grouped["rebalance_interval"] = df_grouped["dateTime"].diff().abs().dt.total_seconds()


        # Compute rebalance frequency statistics
        total_rebalances = df_grouped["rebalance_interval"].count()
        avg_interval = df_grouped["rebalance_interval"].mean()
        median_interval = df_grouped["rebalance_interval"].median()
        min_interval = df_grouped["rebalance_interval"].min()
        max_interval = df_grouped["rebalance_interval"].max()

        # Calculate frequency per day
        total_duration = (df_grouped["dateTime"].max() - df_grouped["dateTime"].min()).total_seconds()
        days = total_duration / 86400  # Convert seconds to days
        frequency_per_day = total_rebalances / days if days > 0 else 0  # Avoid division by zero

        # Fetch latest token prices
        prices = fetch_token_prices()
        if not prices:
            print("Could not fetch token prices. Exiting.")
            return

        # Calculate total added liquidity in USD
        total_added_liquidity_usd = (ws_transfers * prices["wS_price"]) + (usdce_transfers * prices["USDC.e_price"])

        # Calculate total rewards earned in USD
        total_rewards_usd = (shadow_rewards * prices["SHADOW_price"]) + (xshadow_rewards * prices["xSHADOW_price"])

        # Liquidity duration from first transaction to current time
        # Ensure first_transaction_time is timezone-aware
        first_transaction_time = df_grouped["dateTime"].min()
        if first_transaction_time.tzinfo is None:
            first_transaction_time = first_transaction_time.replace(tzinfo=timezone.utc)  # Make it timezone-aware

        # Current time is already timezone-aware
        current_time = datetime.now(timezone.utc)

        # Calculate the difference
        liquidity_duration_days = (current_time - first_transaction_time).total_seconds() / 86400


        # APR Calculation
        apr = (total_rewards_usd / total_added_liquidity_usd) * (365 / liquidity_duration_days) * 100 if liquidity_duration_days > 0 else 0

        # Print results in a readable format
        results = [
            f"\n=== Rebalance Frequency Statistics ===",
            f"Total Rebalance Events: {total_rebalances}",
            f"Average Interval: {avg_interval:.2f} seconds (~{avg_interval / 3600:.2f} hours)",
            f"Median Interval: {median_interval:.2f} seconds (~{median_interval / 3600:.2f} hours)",
            f"Minimum Interval: {min_interval:.2f} seconds",
            f"Maximum Interval: {max_interval:.2f} seconds (~{max_interval / 3600:.2f} hours)",
            f"Rebalance Frequency per Day: {frequency_per_day:.2f} rebalances/day",
            f"\n=== Liquidity & APR Calculation ===",
            f"Total Added Liquidity (USD): ${total_added_liquidity_usd:.2f}",
            f"Total Rewards Earned (USD): ${total_rewards_usd:.2f}",
            f"Liquidity Duration: {liquidity_duration_days:.2f} days",
            f"APR: {apr:.2f}%"
        ]
        print(results)
        for result in results:
            log_to_file(result)

    except FileNotFoundError:
        print(f"Error: File liquidity_{user_address}.csv not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

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

log_to_file(f"Total wS added liquidity: {ws_transfers:.6f}")
log_to_file(f"Total USDC.e added liquidity: {usdce_transfers:.6f}")


# FETCH REWARDS TRANSACTIONS
# Fetch transactions for both SHADOW and xSHADOW
shadow_transactions = fetch_transactions(SHADOW_ADDRESS, user_address)
xshadow_transactions = fetch_transactions(XSHADOW_ADDRESS, user_address)

rewards_transactions = shadow_transactions + xshadow_transactions

df_rewards = pd.DataFrame(rewards_transactions)

# Convert from Wei to Ether
df_rewards["value"] = df_rewards["value"].astype(float) * 10**-18

# Filter by recipient address
df_rewards["from"] = df_rewards["from"].str.lower()
df_rewards_filtered = df_rewards[df_rewards["from"] == SENDER_ADDRESS.lower()]

# Calculate total rewards for both tokens separately
shadow_rewards = df_rewards_filtered[df_rewards_filtered["tokenSymbol"] == "SHADOW"]["value"].sum()
xshadow_rewards = df_rewards_filtered[df_rewards_filtered["tokenSymbol"] == "xSHADOW"]["value"].sum()

output_file = f"rewards_{user_address}.csv"
df_rewards_filtered.to_csv(output_file, index=False)

print(f"Filtered transactions saved to {output_file}")
print(f"Total $SHADOW tokens received: {shadow_rewards:.6f}")
print(f"Total $xSHADOW tokens received: {xshadow_rewards:.6f}")

log_to_file(f"Total $SHADOW tokens received: {shadow_rewards:.6f}")
log_to_file(f"Total $xSHADOW tokens received: {xshadow_rewards:.6f}")

calculate_rebalance_frequency_and_apr(user_address, ws_transfers, usdce_transfers, shadow_rewards, xshadow_rewards)
