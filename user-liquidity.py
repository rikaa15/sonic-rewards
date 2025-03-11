import requests
import pandas as pd
import time

API_KEY = ""  # Replace with your API key
USDCE_ADDRESS = "0x29219dd400f2Bf60E5a23d13Be72B486D4038894"  # USDC.e token
WS_ADDRESS = "0x039e2fB66102314Ce7b64Ce5Ce3E5183bc94aD38"  # wS token
POOL_ADDRESS = "0x324963c267C354c7660Ce8CA3F5f167E05649970"  # Pool address
BASE_URL = "https://api.sonicscan.org/api"
OFFSET = 1000 
ALL_TRANSACTIONS = []

START_BLOCK = 0
END_BLOCK = 99999999
BLOCK_STEP = 500000 

# Prompt user for the recipient address to filter
user_address = input("Enter the recipient address to filter transactions: ").strip().lower()

current_start = START_BLOCK

# Function to fetch transactions for a given token
def fetch_transactions(token_address, token_symbol):
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
                "address": user_address,
                "page": page,
                "offset": OFFSET,
                "startblock": current_start,
                "endblock": current_end,
                "sort": "asc",
                "apikey": API_KEY
            }

            try:
                response = requests.get(BASE_URL, params=params).json()
                
                # Check if response contains results
                if "result" in response and response["result"]:
                    # Add token name to distinguish the tokens
                    print(response["result"])
                    all_transactions.extend(response["result"])
                    page += 1
                else:
                    break

                # Add a small delay to prevent hitting rate limits
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                break

        current_start += BLOCK_STEP

    return all_transactions

# Fetch transactions for both wS and USDC.e
ws_transactions = fetch_transactions(WS_ADDRESS, "wS")
usdce_transactions = fetch_transactions(USDCE_ADDRESS, "USDC.e")

all_transactions = ws_transactions + usdce_transactions

# Convert to DataFrame
df = pd.DataFrame(all_transactions)

df["value"] = df["value"].astype(float)
df["value"] = df.apply(
    lambda row: row["value"] * 10**-18 if row["tokenSymbol"] == "wS" else row["value"] * 10**-6, axis=1
)


# Filter for transactions where POOL_ADDRESS is either 'from' or 'to'
df_filtered = df[(df["from"].str.lower() == POOL_ADDRESS.lower()) | (df["to"].str.lower() == POOL_ADDRESS.lower())]

output_file = f"liquidity_{user_address}.csv"
df_filtered.to_csv(output_file, index=False)

print(f"Filtered transactions saved to {output_file}")

# Calculate total transfers for both tokens separately
ws_transfers = df_filtered[df_filtered["tokenSymbol"] == "wS"].apply(
    lambda row: -row["value"] if row["from"].lower() == POOL_ADDRESS.lower() and row["to"].lower() == user_address.lower()
    else row["value"] if row["from"].lower() == user_address.lower() and row["to"].lower() == POOL_ADDRESS.lower()
    else 0,
    axis=1
).sum()

usdce_transfers = df_filtered[df_filtered["tokenSymbol"] == "USDC.e"].apply(
    lambda row: -row["value"] if row["from"].lower() == POOL_ADDRESS.lower() and row["to"].lower() == user_address.lower()
    else row["value"] if row["from"].lower() == user_address.lower() and row["to"].lower() == POOL_ADDRESS.lower()
    else 0,
    axis=1
).sum()

print(f"Total wS added liquidity: {ws_transfers:.6f}")
print(f"Total USDC.e added liquidity: {usdce_transfers:.6f}")

def calculate_rebalancing_frequency(df_filtered, time_period='D'):
    # Extract the timestamps of the filtered transactions
    rebalance_dates = pd.to_datetime(df_filtered["timeStamp"], unit='s')

    # Create a DataFrame of rebalance timestamps
    df_rebalance = pd.DataFrame(rebalance_dates, columns=["timestamp"])

    # Set timestamp as the index and resample based on the time period (e.g., daily, weekly)
    df_rebalance.set_index("timestamp", inplace=True)
    df_resampled = df_rebalance.resample(time_period).count()

    return df_resampled

# Calculate rebalancing frequency for wS and USDC.e over time
ws_rebalance_frequency = calculate_rebalancing_frequency(df_filtered[df_filtered["tokenSymbol"] == "wS"], time_period='D')  # Daily
usdce_rebalance_frequency = calculate_rebalancing_frequency(df_filtered[df_filtered["tokenSymbol"] == "USDC.e"], time_period='D')  # Daily

# Display the rebalancing frequency
print(f"\nRebalancing frequency for wS (daily):")
print(ws_rebalance_frequency)
print(f"\nRebalancing frequency for USDC.e (daily):")
print(usdce_rebalance_frequency)