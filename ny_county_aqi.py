import pandas as pd

# Load your full AQI dataset (use the daily 1980–2021 one you filtered)
df = pd.read_csv("aqi_daily_1980_to_2021_New_York.csv", parse_dates=["Date"])

# Ensure column names are consistent
df = df.rename(columns={
    "County Name": "County",
    "Date": "date",
    "AQI": "AQI"
})

# Filter only New York (safety check)
df = df[df["State Name"] == "New York"]

# Monthly average AQI per county
monthly_county = (
    df.groupby([pd.Grouper(key="date", freq="M"), "County"])["AQI"]
      .mean()
      .reset_index()
      .rename(columns={"AQI": "County_AQI"})
)

# Sort for readability
monthly_county = monthly_county.sort_values(["County", "date"])

# Save output
monthly_county.to_csv("ny_monthly_county_aqi.csv", index=False)

print("Created ny_monthly_county_aqi.csv")
print(monthly_county.head(10))
