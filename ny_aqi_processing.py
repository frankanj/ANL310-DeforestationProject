import pandas as pd

# Load your filtered NY data
aqi = pd.read_csv("aqi_daily_1980_to_2021_New_York.csv")

# Convert Date to datetime
aqi["Date"] = pd.to_datetime(aqi["Date"])

# Limit to 2010–2021
aqi = aqi[(aqi["Date"] >= "2010-01-01") & (aqi["Date"] <= "2021-12-31")]

# --- 1. Monthly AQI per county ----------------------------------------------
# Group by county + month, compute mean AQI
monthly_county = (
    aqi
    .set_index("Date")
    .groupby("County Name")["AQI"]
    .resample("MS")
    .mean()
    .reset_index()
    .rename(columns={"AQI": "County_AQI", "Date": "date"})
)

# --- 2. Monthly statewide NY AQI (mean across all counties) -----------------
monthly_statewide = (
    aqi
    .set_index("Date")
    .resample("MS")["AQI"]
    .mean()
    .reset_index()
    .rename(columns={"AQI": "NY_AQI", "Date": "date"})
)

# ---------- Monthly AQI per county ----------
monthly_county = (
    aqi
    .set_index("Date")
    .groupby("County Name")["AQI"]
    .resample("MS")
    .mean()
    .reset_index()
    .rename(columns={"AQI": "County_AQI", "Date": "date"})
)

# ---------- Monthly statewide AQI ----------
monthly_statewide = (
    aqi
    .set_index("Date")
    .resample("MS")["AQI"]
    .mean()
    .reset_index()
    .rename(columns={"AQI": "NY_AQI", "Date": "date"})
)

print("\nMonthly County-Level AQI:")
print(monthly_county.head(20))

print("\nMonthly Statewide AQI:")
print(monthly_statewide.head(20))

print("\nCounty-level structure:")
print(monthly_county.info())

print("\nStatewide structure:")
print(monthly_statewide.info())

monthly_statewide.to_csv("monthly_statewide.csv", index=False)