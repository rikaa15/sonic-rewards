import pandas as pd

df = pd.read_csv("filtered_transactions.csv")

df["value"] = pd.to_numeric(df["value"])

# Group by recipient address and sum the received tokens
top_recipient = df.groupby("to")["value"].sum().sort_values(ascending=False)

# Print top 10 recipients
print(top_recipient.head(10))
