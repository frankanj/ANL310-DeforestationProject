import pandas as pd

# Load or reuse the existing dataframes:
# monthly_on, monthly_qc, monthly_nl, monthly_statewide

# 1. Merge Ontario + Québec + Newfoundland into one table
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

print("\nVIF ALL (Ontario + Québec + NL):")
print(vif_all.head(20))
print(vif_all.tail(20))
print(vif_all.info())

# 2. Merge with New York statewide AQI
merged_ny_vif = vif_all.merge(monthly_statewide, on="date", how="inner")

print("\nMerged NY AQI + VIF table:")
print(merged_ny_vif.head(20))
print(merged_ny_vif.tail(20))
print(merged_ny_vif.info())
