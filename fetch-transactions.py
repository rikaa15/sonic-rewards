import requests
import pandas as pd

API_KEY = ""  # Replace with your API key
CONTRACT_ADDRESS = "0x3333b97138D4b086720b5aE8A7844b1345a33333"
SENDER_ADDRESS = "0x0ac98Ce57D24f77F48161D12157cb815Af469fc0"
BASE_URL = "https://api.sonicscan.org/api"
OFFSET = 1000  # Max transactions per request
ALL_TRANSACTIONS = []

START_BLOCK = 0
END_BLOCK = 99999999
BLOCK_STEP = 500000  # API limit adjustment

current_start = START_BLOCK

while current_start <= END_BLOCK:
    current_end = min(current_start + BLOCK_STEP, END_BLOCK)
    page = 1

    while True:
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": CONTRACT_ADDRESS,
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
            ALL_TRANSACTIONS.extend(response["result"])
            page += 1
        else:
            break

    current_start += BLOCK_STEP

df = pd.DataFrame(ALL_TRANSACTIONS)

# Convert "value" column from Wei to Ether
df["value"] = df["value"].astype(float) * 10**-18

# Save to CSV
df.to_csv("filtered_transactions.csv", index=False)

print("All transactions saved to filtered_transactions.csv")
