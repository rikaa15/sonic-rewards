import pandas as pd
import requests
from datetime import datetime, timezone

def fetch_token_prices():
    """Fetch latest prices of wS, USDC.e, SHADOW, and xSHADOW tokens"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": ""  # Your CoinGecko API Key
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
            "USDC.e_price": data.get("sonic-bridged-usdc-e-sonic", {}).get("usd", 1),  # USDC ~1 USD
            "SHADOW_price": data.get("shadow-2", {}).get("usd", 0),
            "xSHADOW_price": data.get("shadow-2", {}).get("usd", 0)  # Assuming xSHADOW = SHADOW price
        }
    except Exception as e:
        print(f"Error fetching token prices: {e}")
        return None

def calculate_rebalance_frequency_and_apr(address):
    # Construct the filename based on the address
    file_path = f"liquidity_{address}.csv"

    try:
        # Load the file into a DataFrame
        df = pd.read_csv(file_path)

        # Convert timestamp to datetime format
        df["dateTime"] = pd.to_datetime(df["timeStamp"], unit="s")

        # Sort by timestamp
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

        # Get user inputs for added liquidity and rewards received
        wS_amount = float(input("Enter wS added liquidity amount: "))
        USDC_amount = float(input("Enter USDC.e added liquidity amount: "))
        SHADOW_amount = float(input("Enter SHADOW tokens received: "))
        xSHADOW_amount = float(input("Enter xSHADOW tokens received: "))

        # Fetch latest token prices
        prices = fetch_token_prices()
        if not prices:
            print("Could not fetch token prices. Exiting.")
            return

        # Calculate total added liquidity in USD
        total_added_liquidity_usd = (wS_amount * prices["wS_price"]) + (USDC_amount * prices["USDC.e_price"])

        # Calculate total rewards earned in USD
        total_rewards_usd = (SHADOW_amount * prices["SHADOW_price"]) + (xSHADOW_amount * prices["xSHADOW_price"])

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
        print("\n=== Rebalance Frequency Statistics ===")
        print(f"Total Rebalance Events: {total_rebalances}")
        print(f"Average Interval: {avg_interval:.2f} seconds (~{avg_interval / 3600:.2f} hours)")
        print(f"Median Interval: {median_interval:.2f} seconds (~{median_interval / 3600:.2f} hours)")
        print(f"Minimum Interval: {min_interval:.2f} seconds")
        print(f"Maximum Interval: {max_interval:.2f} seconds (~{max_interval / 3600:.2f} hours)")
        print(f"Rebalance Frequency per Day: {frequency_per_day:.2f} rebalances/day")

        print("\n=== Liquidity & APR Calculation ===")
        print(f"Total Added Liquidity (USD): ${total_added_liquidity_usd:.2f}")
        print(f"Total Rewards Earned (USD): ${total_rewards_usd:.2f}")
        print(f"Liquidity Duration: {liquidity_duration_days:.2f} days")
        print(f"APR: {apr:.2f}%")

    except FileNotFoundError:
        print(f"Error: File liquidity_{address}.csv not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Get user input for Ethereum address
eth_address = input("Enter Ethereum address: ").strip()

# Calculate and display rebalance statistics and APR
calculate_rebalance_frequency_and_apr(eth_address)
