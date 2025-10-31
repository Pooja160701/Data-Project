import pandas as pd

master_df = pd.read_csv("MasterDB.csv")
new_df = pd.read_csv("NewData.csv")

print("MasterDB Columns:", master_df.columns.tolist())
print("NewData Columns:", new_df.columns.tolist())
