import pandas as pd

# Load cleaned monthly datasets
monthly_on = pd.read_csv("monthly_on.csv", parse_dates=["date"])
monthly_qc = pd.read_csv("monthly_qc.csv", parse_dates=["date"])
monthly_nl = pd.read_csv("monthly_nl.csv", parse_dates=["date"])
monthly_statewide = pd.read_csv("monthly_statewide.csv", parse_dates=["date"])

# Merge all provinces into one VIF table
vif_all = (
    monthly_on[["date","VIF_count"]].rename(columns={"VIF_count":"Ontario_VIF"})
    .merge(
        monthly_qc[["date","VIF_count"]].rename(columns={"VIF_count":"Quebec_VIF"}),
        on="date",
        how="outer"
    )
    .merge(
        monthly_nl[["date","VIF_count"]].rename(columns={"VIF_count":"NL_VIF"}),
        on="date",
        how="outer"
    )
    .sort_values("date")
)

print("VIF ALL preview:")
print(vif_all.head())
print(vif_all.tail())

# Merge with NY AQI statewide
merged_ny_vif = vif_all.merge(monthly_statewide, on="date", how="inner")

print("\nMerged NY AQI + All Provinces:")
print(merged_ny_vif.head())
print(merged_ny_vif.tail())

merged_ny_vif.to_csv("merged_ny_vif.csv", index=False)
