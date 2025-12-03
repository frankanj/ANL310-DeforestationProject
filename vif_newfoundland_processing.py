import pandas as pd
import zipfile

# --------- NEWFOUNDLAND VIF: weekly -> monthly ---------
zip_path_nl = "Historical Fire Alerts in Newfoundland and Labrador, Canada.zip"

with zipfile.ZipFile(zip_path_nl) as z:
    inner_name = z.namelist()[0]
    with z.open(inner_name) as f:
        nl_raw = pd.read_csv(f)

print("Newfoundland raw columns:", nl_raw.columns.tolist())
print(nl_raw.head())

# Standardize column names
nl = nl_raw.copy()
nl = nl.rename(columns=str.strip)

year_col = "alert__year"
week_col = "alert__week"
count_col = "alert__count"

# Filter years 2010–2021
nl = nl[(nl[year_col] >= 2010) & (nl[year_col] <= 2021)]

# Create ISO week date
nl["year_str"] = nl[year_col].astype(int).astype(str)
nl["week_str"] = nl[week_col].astype(int).astype(str).str.zfill(2)

nl["date"] = pd.to_datetime(
    nl["year_str"] + "-W" + nl["week_str"] + "-1",
    format="%G-W%V-%u",
    errors="coerce"
)

nl = nl.dropna(subset=["date"])

# Weekly aggregation
weekly_nl = (
    nl.groupby("date", as_index=False)[count_col]
      .sum()
      .rename(columns={count_col: "VIF_count"})
)

print("\nNewfoundland weekly VIF preview:")
print(weekly_nl.head())

# Monthly aggregation
monthly_nl = (
    weekly_nl
    .set_index("date")
    .resample("MS")["VIF_count"]
    .sum()
    .reset_index()
)

monthly_nl["Region"] = "Newfoundland and Labrador"

print("\nNewfoundland monthly VIF preview:")
print(monthly_nl.head(12))
print("\nNewfoundland monthly structure:")
print(monthly_nl.info())

monthly_nl.to_csv("monthly_nl.csv", index=False)