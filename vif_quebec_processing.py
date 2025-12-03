import pandas as pd
import zipfile

# --------- QUÉBEC VIF: weekly -> monthly ---------
zip_path_qc = "Historical Fire Alerts in Québec, Canada.zip"

# 1) Read CSV inside zip
with zipfile.ZipFile(zip_path_qc) as z:
    inner_name = z.namelist()[0]   # if this errors, print(z.namelist()) once
    with z.open(inner_name) as f:
        qc_raw = pd.read_csv(f)

print("Québec raw columns:", qc_raw.columns.tolist())
print(qc_raw.head())

# Standardize column names
qc = qc_raw.copy()
qc = qc.rename(columns=str.strip)

year_col = "alert__year"
week_col = "alert__week"
count_col = "alert__count"

# Filter years 2010–2021
qc = qc[(qc[year_col] >= 2010) & (qc[year_col] <= 2021)]

# Build ISO week date
qc["year_str"] = qc[year_col].astype(int).astype(str)
qc["week_str"] = qc[week_col].astype(int).astype(str).str.zfill(2)

qc["date"] = pd.to_datetime(
    qc["year_str"] + "-W" + qc["week_str"] + "-1",
    format="%G-W%V-%u",
    errors="coerce"
)

qc = qc.dropna(subset=["date"])

# Weekly VIF totals
weekly_qc = (
    qc.groupby("date", as_index=False)[count_col]
      .sum()
      .rename(columns={count_col: "VIF_count"})
)

print("\nQuébec weekly VIF preview:")
print(weekly_qc.head())

# Monthly totals
monthly_qc = (
    weekly_qc
    .set_index("date")
    .resample("MS")["VIF_count"]
    .sum()
    .reset_index()
)

monthly_qc["Region"] = "Quebec"

print("\nQuébec monthly VIF preview:")
print(monthly_qc.head(12))
print("\nQuébec monthly structure:")
print(monthly_qc.info())

monthly_qc.to_csv("monthly_qc.csv", index=False)