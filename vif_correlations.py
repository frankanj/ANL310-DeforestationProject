import pandas as pd

# Load merged dataset
df = pd.read_csv("merged_ny_vif.csv", parse_dates=["date"])

# Columns to test
vif_cols = ["Ontario_VIF", "Quebec_VIF", "NL_VIF"]

# STORE RESULTS
results = {}

# -------------------------------
# 0-LAG CORRELATIONS
# -------------------------------
corr_0 = df[vif_cols + ["NY_AQI"]].corr()["NY_AQI"].drop("NY_AQI")
results["lag_0"] = corr_0

# -------------------------------
# LAG CORRELATIONS (1–6 months)
# -------------------------------
max_lag = 6
for lag in range(1, max_lag + 1):
    lagged_df = df.copy()
    lagged_df["NY_AQI_lag"] = lagged_df["NY_AQI"].shift(-lag)

    corr_lag = lagged_df[vif_cols + ["NY_AQI_lag"]].corr()["NY_AQI_lag"].drop("NY_AQI_lag")
    results[f"lag_{lag}"] = corr_lag

# -------------------------------
# PRINT CLEAN TABLE
# -------------------------------
print("\n=== Correlation of VIF Alerts vs New York AQI ===\n")
print("Positive value = higher VIF associated with higher AQI")
print("Negative value = higher VIF associated with lower AQI\n")

correlation_table = pd.DataFrame(results)
print(correlation_table.round(3))
