import requests
import pandas as pd

API_KEY = ""  # Replace with your API key
SHADOW_ADDRESS = "0x3333b97138D4b086720b5aE8A7844b1345a33333"  # SHADOW token
XSHADOW_ADDRESS = "0x5050bc082FF4A74Fb6B0B04385dEfdDB114b2424"  # xSHADOW token
SENDER_ADDRESS = "0x0ac98Ce57D24f77F48161D12157cb815Af469fc0"  # Gauge address
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
def fetch_transactions(token_address, token_name):
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
                "address": SENDER_ADDRESS,
                "page": page,
                "offset": OFFSET,
                "startblock": current_start,
                "endblock": current_end,
                "sort": "asc",
                "apikey": API_KEY
            }

            response = requests.get(BASE_URL, params=params).json()

            if "result" in response and response["result"]:
                # Add token name to distinguish the tokens
                for txn in response["result"]:
                    txn["token_name"] = token_name
                all_transactions.extend(response["result"])
                page += 1
            else:
                break

        current_start += BLOCK_STEP

    return all_transactions

# Fetch transactions for both SHADOW and xSHADOW
shadow_transactions = fetch_transactions(SHADOW_ADDRESS, "SHADOW")
xshadow_transactions = fetch_transactions(XSHADOW_ADDRESS, "xSHADOW")

all_transactions = shadow_transactions + xshadow_transactions

df = pd.DataFrame(all_transactions)

# Convert from Wei to Ether
df["value"] = df["value"].astype(float) * 10**-18

# Filter by recipient address
df["to"] = df["to"].str.lower()
df_filtered = df[df["to"] == user_address]

# Calculate total rewards for both tokens separately
shadow_rewards = df_filtered[df_filtered["token_name"] == "SHADOW"]["value"].sum()
xshadow_rewards = df_filtered[df_filtered["token_name"] == "xSHADOW"]["value"].sum()

output_file = f"rewards_{user_address}.csv"
df_filtered.to_csv(output_file, index=False)

print(f"Filtered transactions saved to {output_file}")
print(f"Total $SHADOW tokens received by {user_address}: {shadow_rewards:.6f} tokens")
print(f"Total $xSHADOW tokens received by {user_address}: {xshadow_rewards:.6f} tokens")
