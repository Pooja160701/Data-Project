import pandas as pd
import numpy as np

master = pd.read_csv(r"E:\Data Project\Question2\MasterDB.csv")
new = pd.read_csv(r"E:\Data Project\Question2\NewData.csv")


for df in [master, new]:
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

def normalize_status(s):
    if pd.isna(s):
        return ""
    s = str(s).strip().lower()
    if "avail" in s:
        return "available"
    if "sold" in s:
        return "sold"
    return s

master["Status"] = master["Status"].apply(normalize_status)
new["Status"] = new["Status"].apply(normalize_status)

new.replace(r"^\s*(N\.?A\.?|n/a|\-)\s*$", np.nan, regex=True, inplace=True)
master.replace(r"^\s*(N\.?A\.?|n/a|\-)\s*$", np.nan, regex=True, inplace=True)

key_cols = ["Car Name", "Manufactured", "COE"]

sold_keys = new.loc[new["Status"] == "sold", key_cols].drop_duplicates()
if not sold_keys.empty:
    master = master.merge(sold_keys, on=key_cols, how="left", indicator=True)
    master = master[master["_merge"] == "left_only"].drop(columns=["_merge"])

valid_new = new[
    (new["Status"] == "available")
    & (~new["Price"].isna())
    & (~new["COE"].isna())
].copy()

merged = pd.merge(
    master,
    valid_new,
    on=key_cols,
    how="outer",
    suffixes=("_master", "_new"),
    indicator=True
)

final = pd.DataFrame()
for col in master.columns:
    if col in key_cols:
        final[col] = merged[col]
    else:
        col_master = f"{col}_master"
        col_new = f"{col}_new"
        if col_master in merged.columns and col_new in merged.columns:
            final[col] = merged[col_new].combine_first(merged[col_master])
        elif col_master in merged.columns:
            final[col] = merged[col_master]
        elif col_new in merged.columns:
            final[col] = merged[col_new]

final = final[final["Status"] != "sold"]

final.drop_duplicates(subset=key_cols, keep="last", inplace=True)

final.to_csv("Updated_MasterDB.csv", index=False)

added = merged["_merge"].eq("right_only").sum()
updated = merged["_merge"].eq("both").sum()
removed = len(sold_keys)

print("MasterDB successfully updated and saved as 'Updated_MasterDB.csv'")
print(f"Added {added} new rows")
print(f"Updated {updated} existing rows")
print(f"Removed {removed} sold rows")
