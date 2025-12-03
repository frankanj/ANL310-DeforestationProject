import pandas as pd
import matplotlib.pyplot as plt

# Load merged dataset (output from your merge script)
merged_ny_vif = pd.read_csv("merged_ny_vif.csv", parse_dates=["date"])

# ------------- LOG-SCALE PLOT: FULL SPIKES ----------------
fig, ax1 = plt.subplots(figsize=(12, 6))

# VIF lines (Ontario, Quebec, Newfoundland & Labrador)
line_on, = ax1.plot(merged_ny_vif["date"], merged_ny_vif["Ontario_VIF"],
                    label="Ontario VIF", linewidth=2)
line_qc, = ax1.plot(merged_ny_vif["date"], merged_ny_vif["Quebec_VIF"],
                    label="Quebec VIF", linewidth=2)
line_nl, = ax1.plot(merged_ny_vif["date"], merged_ny_vif["NL_VIF"],
                    label="NL VIF", linewidth=2)

ax1.set_ylabel("VIF Count (log scale)")
ax1.set_xlabel("Date")
ax1.set_yscale("log")

max_val = merged_ny_vif[["Ontario_VIF", "Quebec_VIF", "NL_VIF"]].to_numpy().max()
ax1.set_ylim(1, max_val * 1.2)

ax1.grid(True, which="both", linestyle="--", linewidth=0.5)

# NY AQI on secondary axis
ax2 = ax1.twinx()
line_aqi, = ax2.plot(merged_ny_vif["date"], merged_ny_vif["NY_AQI"],
                     linestyle="--", linewidth=2, color="black", label="NY AQI")
ax2.set_ylabel("NY AQI")

# Legend above the plot
lines = [line_on, line_qc, line_nl, line_aqi]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels,
           loc="upper center",
           bbox_to_anchor=(0.5, 1.12),
           ncol=4,
           framealpha=0.9)

ax1.set_title("Monthly VIF Alerts (ON, QC, NL) vs New York AQI (Log Scale)")
plt.tight_layout()
plt.show()