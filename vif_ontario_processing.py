import pandas as pd
import zipfile

# --------- ONTARIO VIF: weekly -> monthly ---------
zip_path_on = "Historical Fire Alerts in Ontario, Canada.zip"

# 1) Read the CSV inside the zip
with zipfile.ZipFile(zip_path_on) as z:
    # adjust the inner filename if this errors; print(z.namelist()) to see options
    inner_name = z.namelist()[0]
    with z.open(inner_name) as f:
        on_raw = pd.read_csv(f)

print("Ontario raw columns:", on_raw.columns.tolist())
print(on_raw.head())

# 2) Keep just what we need and restrict years
# adjust column names here if they differ
on = on_raw.copy()
on = on.rename(columns=str.strip)

# try to use these typical column names; change if your printout shows something else
year_col = "alert__year"
week_col = "alert__week"
count_col = "alert__count"

on = on[(on[year_col] >= 2010) & (on[year_col] <= 2021)]

# 3) Convert (year, week) to a real date – Monday of ISO week
on["year_str"] = on[year_col].astype(int).astype(str)
on["week_str"] = on[week_col].astype(int).astype(str).str.zfill(2)

on["date"] = pd.to_datetime(
    on["year_str"] + "-W" + on["week_str"] + "-1",
    format="%G-W%V-%u",
    errors="coerce"
)

on = on.dropna(subset=["date"])

# 4) Weekly total alerts
weekly_on = (
    on.groupby("date", as_index=False)[count_col]
      .sum()
      .rename(columns={count_col: "VIF_count"})
)

print("\nOntario weekly VIF preview:")
print(weekly_on.head())

# 5) Monthly total alerts (sum of weekly counts in each month)
monthly_on = (
    weekly_on
    .set_index("date")
    .resample("MS")["VIF_count"]
    .sum()
    .reset_index()
)

monthly_on["Region"] = "Ontario"

print("\nOntario monthly VIF preview:")
print(monthly_on.head(12))
print("\nOntario monthly structure:")
print(monthly_on.info())
