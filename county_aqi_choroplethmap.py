import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
SHAPEFILE_PATH = r"shapefiles/cb_2018_us_county_5m/cb_2018_us_county_5m.shp"
COUNTY_AQI_CSV = r"ny_monthly_county_aqi.csv"
MERGED_VIF_CSV = r"merged_ny_vif.csv"   # for the VIF vs AQI panel
FRAMES_DIR = r"a qi_frames"             # folder for animation frames
os.makedirs(FRAMES_DIR, exist_ok=True)

# Downstate vs Upstate split for regional averages
DOWNSTATE_COUNTIES = {
    "New York", "Kings", "Queens", "Bronx", "Richmond",
    "Nassau", "Suffolk", "Westchester", "Rockland", "Putnam"
}

# -------------------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------------------
def load_data():
    aqi = pd.read_csv(COUNTY_AQI_CSV, parse_dates=["date"])
    counties = gpd.read_file(SHAPEFILE_PATH)

    # Keep only New York
    ny_counties = counties[counties["STATEFP"] == "36"].copy()
    ny_counties["County"] = ny_counties["NAME"].str.strip()

    # Small cleanup
    aqi["County"] = aqi["County"].str.strip()
    return aqi, ny_counties


# -------------------------------------------------------------------
# 1. STATIC MAP FOR A GIVEN YEAR/MONTH + PNG + LABELS
# -------------------------------------------------------------------
def plot_static_map(target_year=2020, target_month=None, save_png=True):
    """
    target_month: 1-12 or None.
      - If None: plot YEAR AVERAGE
      - Else: plot that specific month of that year
    """
    aqi, ny_counties = load_data()

    if target_month is None:
        # Yearly average per county
        aqi_sel = (
            aqi[aqi["date"].dt.year == target_year]
            .groupby("County", as_index=False)["County_AQI"].mean()
        )
        title_suffix = f"Average AQI {target_year}"
    else:
        mask = (aqi["date"].dt.year == target_year) & (aqi["date"].dt.month == target_month)
        aqi_sel = aqi[mask].copy()
        aqi_sel = aqi_sel.groupby("County", as_index=False)["County_AQI"].mean()
        title_suffix = f"AQI {target_year}-{target_month:02d}"

    merged = ny_counties.merge(aqi_sel, on="County", how="left")

    fig, ax = plt.subplots(1, 1, figsize=(8, 9))
    merged.plot(
        ax=ax,
        column="County_AQI",
        cmap="YlOrRd",
        legend=True,
        edgecolor="black",
        linewidth=0.4,
        missing_kwds={"color": "lightgrey", "label": "No data"},
    )

    ax.set_title(f"New York County AQI — {title_suffix}", fontsize=16)
    ax.axis("off")

    # Label top 5 worst counties to avoid clutter
    top5 = aqi_sel.sort_values("County_AQI", ascending=False).head(5)["County"].tolist()
    merged_lab = merged[merged["County"].isin(top5)].to_crs(epsg=3857)
    for _, row in merged_lab.iterrows():
        x, y = row["geometry"].centroid.coords[0]
        ax.text(x, y, row["County"], fontsize=8, ha="center", va="center")

    plt.tight_layout()

    if save_png:
        out_name = f"ny_county_aqi_{title_suffix.replace(' ', '_').replace(':', '')}.png"
        plt.savefig(out_name, dpi=300)
        print(f"Saved {out_name}")

    plt.show()


# -------------------------------------------------------------------
# 2. ANIMATION FRAMES: ONE PNG PER MONTH
# -------------------------------------------------------------------
def make_animation_frames(start_year=2015, end_year=2021):
    """
    Generates one PNG per (year, month) in FRAMES_DIR.
    You can stitch them into a GIF with imagemagick/ffmpeg later.
    """
    aqi, ny_counties = load_data()

    # We’ll iterate over unique year-month combinations
    aqi["Year"] = aqi["date"].dt.year
    aqi["Month"] = aqi["date"].dt.month

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            sub = aqi[(aqi["Year"] == year) & (aqi["Month"] == month)]
            if sub.empty:
                continue

            aqi_sel = sub.groupby("County", as_index=False)["County_AQI"].mean()
            merged = ny_counties.merge(aqi_sel, on="County", how="left")

            fig, ax = plt.subplots(1, 1, figsize=(6, 7))
            merged.plot(
                ax=ax,
                column="County_AQI",
                cmap="YlOrRd",
                legend=False,
                edgecolor="black",
                linewidth=0.25,
                missing_kwds={"color": "lightgrey"},
            )
            ax.set_title(f"NY County AQI — {year}-{month:02d}", fontsize=12)
            ax.axis("off")
            plt.tight_layout()

            frame_path = os.path.join(FRAMES_DIR, f"ny_aqi_{year}_{month:02d}.png")
            plt.savefig(frame_path, dpi=150)
            plt.close(fig)

            print(f"Saved frame {frame_path}")

    print("Done generating frames. Use ffmpeg or an online tool to make a GIF.")


# -------------------------------------------------------------------
# 3. REGIONAL AVERAGES (UPSTATE vs DOWNSTATE)
# -------------------------------------------------------------------
def plot_regional_averages():
    aqi, _ = load_data()

    def classify_region(county):
        return "Downstate" if county in DOWNSTATE_COUNTIES else "Upstate"

    aqi["Region"] = aqi["County"].apply(classify_region)
    region_ts = (
        aqi.groupby(["date", "Region"])["County_AQI"]
        .mean()
        .reset_index()
    )

    pivot = region_ts.pivot(index="date", columns="Region", values="County_AQI")

    plt.figure(figsize=(10, 5))
    plt.plot(pivot.index, pivot["Downstate"], label="Downstate", linewidth=2)
    plt.plot(pivot.index, pivot["Upstate"], label="Upstate", linewidth=2)
    plt.ylabel("Average AQI")
    plt.xlabel("Date")
    plt.title("Upstate vs Downstate New York — Average County AQI")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("ny_upstate_downstate_aqi.png", dpi=300)
    print("Saved ny_upstate_downstate_aqi.png")
    plt.show()


# -------------------------------------------------------------------
# 4. SIDE-BY-SIDE MAP + VIF vs AQI PANEL FOR A GIVEN YEAR
# -------------------------------------------------------------------
def plot_map_with_vif_panel(target_year=2020, target_month=None):
    """
    Left: county AQI map (year average or given month).
    Right: line plot of ON/QC/NL VIF + NY AQI for same year.
    """
    aqi, ny_counties = load_data()
    merged_vif = pd.read_csv(MERGED_VIF_CSV, parse_dates=["date"])

    # ---- county AQI selection ----
    if target_month is None:
        aqi_sel = (
            aqi[aqi["date"].dt.year == target_year]
            .groupby("County", as_index=False)["County_AQI"].mean()
        )
        map_title_suffix = f"Avg {target_year}"
    else:
        mask = (aqi["date"].dt.year == target_year) & (aqi["date"].dt.month == target_month)
        aqi_sel = (
            aqi[mask]
            .groupby("County", as_index=False)["County_AQI"].mean()
        )
        map_title_suffix = f"{target_year}-{target_month:02d}"

    merged_map = ny_counties.merge(aqi_sel, on="County", how="left")

    # ---- time series for that year ----
    vif_year = merged_vif[merged_vif["date"].dt.year == target_year].copy()

    fig, (ax_map, ax_ts) = plt.subplots(1, 2, figsize=(14, 7))

    # Map
    merged_map.plot(
        ax=ax_map,
        column="County_AQI",
        cmap="YlOrRd",
        legend=True,
        edgecolor="black",
        linewidth=0.4,
        missing_kwds={"color": "lightgrey", "label": "No data"},
    )
    ax_map.set_title(f"NY County AQI — {map_title_suffix}")
    ax_map.axis("off")

    # Time series: VIF vs NY AQI
    ax_ts.plot(vif_year["date"], vif_year["Ontario_VIF"], label="Ontario VIF", linewidth=2)
    ax_ts.plot(vif_year["date"], vif_year["Quebec_VIF"], label="Quebec VIF", linewidth=2)
    ax_ts.plot(vif_year["date"], vif_year["NL_VIF"], label="NL VIF", linewidth=2)
    ax_ts.set_ylabel("VIF Count")
    ax_ts.set_xlabel("Date")

    ax2 = ax_ts.twinx()
    ax2.plot(vif_year["date"], vif_year["NY_AQI"], label="NY AQI", linestyle="--", color="black", linewidth=2)
    ax2.set_ylabel("NY AQI")

    lines1, labels1 = ax_ts.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax_ts.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    ax_ts.set_title(f"VIF Alerts vs NY AQI — {target_year}")
    ax_ts.grid(True)

    plt.tight_layout()
    out_name = f"ny_map_vif_panel_{map_title_suffix.replace(' ', '_')}.png"
    plt.savefig(out_name, dpi=300)
    print(f"Saved {out_name}")
    plt.show()


# -------------------------------------------------------------------
# MAIN USAGE EXAMPLES
# -------------------------------------------------------------------
if __name__ == "__main__":
    # 1) One static map (year average)
    plot_static_map(target_year=2020, target_month=None)

    # 2) Regional averages line plot
    plot_regional_averages()

    # 3) Side-by-side map + VIF panel for 2020
    plot_map_with_vif_panel(target_year=2020, target_month=None)

    # 4) OPTIONAL: generate frames for animation
    # make_animation_frames(start_year=2015, end_year=2021)
