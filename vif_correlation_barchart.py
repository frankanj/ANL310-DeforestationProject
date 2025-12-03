import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load correlation results (same computation as before)
df = pd.read_csv("merged_ny_vif.csv", parse_dates=["date"])

vif_cols = ["Ontario_VIF", "Quebec_VIF", "NL_VIF"]

# Compute correlations
results = {}
max_lag = 6

# 0-lag
corr_0 = df[vif_cols + ["NY_AQI"]].corr()["NY_AQI"].drop("NY_AQI")
results["lag_0"] = corr_0

# lags 1–6
for lag in range(1, max_lag + 1):
    lagged = df.copy()
    lagged["NY_AQI_lag"] = lagged["NY_AQI"].shift(-lag)
    corr = lagged[vif_cols + ["NY_AQI_lag"]].corr()["NY_AQI_lag"].drop("NY_AQI_lag")
    results[f"lag_{lag}"] = corr

corr_df = pd.DataFrame(results)

# ---------------------------
# Bar Chart
# ---------------------------
lags = corr_df.columns
x = np.arange(len(lags))  # positions

width = 0.25

fig, ax = plt.subplots(figsize=(12, 6))

# Bars for each province
ax.bar(x - width, corr_df.loc["Ontario_VIF"], width, label="Ontario", color="#1f77b4")
ax.bar(x,         corr_df.loc["Quebec_VIF"],  width, label="Quebec", color="#ff7f0e")
ax.bar(x + width, corr_df.loc["NL_VIF"],      width, label="NL",     color="#2ca02c")

# Labels & formatting
ax.set_ylabel("Correlation Coefficient")
ax.set_xlabel("Lag (Months)")
ax.set_title("Correlation of VIF Alerts with New York AQI (By Lag)")
ax.set_xticks(x)
ax.set_xticklabels(lags)
ax.axhline(0, color="black", linewidth=1)

ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()
