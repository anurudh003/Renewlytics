import pandas as pd
import os
import numpy as np

# =====================================================================
# 1. SET YOUR DATA DIRECTORY
# =====================================================================
DATA_DIR = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\data"

cities = [
    "Delhi","Mumbai","Chennai","Bengaluru","Hyderabad","Kolkata","Jaipur",
    "Ahmedabad","Pune","Kochi","Lucknow","Gandhinagar","Bhopal","Raipur","Guwahati"
]

# =====================================================================
# 2. UNIVERSAL NASA CSV READER — ALWAYS WORKS
# =====================================================================
def read_nasa_csv(path):
    """Reads NASA POWER CSV and extracts Year/Month from DATE column."""
    # Read file ignoring metadata rows
    df = pd.read_csv(path, engine="python", on_bad_lines="skip", encoding="utf-8")
    df.columns = [str(c).strip().upper() for c in df.columns]

    # Detect a DATE column or fallback to first column
    date_col = None
    for c in df.columns:
        if "DATE" in c or "TIME" in c:
            date_col = c
            break

    # If no DATE column exists, assume first column is date-like
    if date_col is None:
        date_col = df.columns[0]

    # Convert to datetime
    df["DATE"] = pd.to_datetime(df[date_col], errors="coerce", infer_datetime_format=True)

    # Extract Year and Month
    df["Year"] = df["DATE"].dt.year
    df["Month"] = df["DATE"].dt.month

    return df

# =====================================================================
# 3. LOAD STATIC CSV FILES
# =====================================================================
sunshine = pd.read_csv(f"{DATA_DIR}/sunshine_india_2015_2024.csv")
cloud = pd.read_csv(f"{DATA_DIR}/cloudcover_india_2015_2024.csv")
population = pd.read_csv(f"{DATA_DIR}/final_population_2015_2024.csv")
energy = pd.read_csv(f"{DATA_DIR}/city_energy_2015_2024.csv")

sunshine.columns = ["City","Year","Month","Sunshine_Hours"]
cloud.columns = ["City","Year","Month","Cloud_Cover"]
population.columns = ["City","Year","Population","Population_Density","Growth_Rate"]
energy.columns = ["City","State","Year","Energy_Consumption_GWh","Per_Capita_kWh","Peak_Demand_MW"]

# Convert types
for df in [sunshine, cloud, population, energy]:
    df["City"] = df["City"].astype(str)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    if "Month" in df.columns:
        df["Month"] = pd.to_numeric(df["Month"], errors="coerce").astype("Int64")

# =====================================================================
# 4. READ ALL SOLAR + WIND FILES
# =====================================================================
solar_frames = []
wind_frames = []

print("\n🔍 Reading NASA solar & wind files...\n")

for city in cities:
    sfile = f"{DATA_DIR}/{city}_solar.csv"
    wfile = f"{DATA_DIR}/{city}_wind.csv"

    # SOLAR
    if os.path.exists(sfile):
        df_s = read_nasa_csv(sfile)
        df_s["City"] = city
        solar_frames.append(df_s)
        print(f"✔ Solar OK: {city}")
    else:
        print(f"❌ Missing Solar: {city}")

    # WIND
    if os.path.exists(wfile):
        df_w = read_nasa_csv(wfile)
        df_w["City"] = city
        wind_frames.append(df_w)
        print(f"✔ Wind OK: {city}")
    else:
        print(f"❌ Missing Wind: {city}")

if not solar_frames:
    raise Exception("❌ ERROR: No solar files loaded.")
if not wind_frames:
    raise Exception("❌ ERROR: No wind files loaded.")

solar_df = pd.concat(solar_frames, ignore_index=True)
wind_df = pd.concat(wind_frames, ignore_index=True)

# =====================================================================
# 5. SELECT RELEVANT COLUMNS (IGNORE MISSING ONES)
# =====================================================================
solar_cols = [
    "City","Year","Month",
    "ALLSKY_SFC_SW_DWN","ALLSKY_SFC_SW_DNI","ALLSKY_SFC_SW_DIFF",
    "T2M","T2M_MAX","T2M_MIN","RH2M","CLD_FRAC","PS"
]
wind_cols = ["City","Year","Month","WS2M","WS10M","WD10M"]

solar_df = solar_df[[c for c in solar_cols if c in solar_df.columns]]
wind_df = wind_df[[c for c in wind_cols if c in wind_df.columns]]

# =====================================================================
# 6. MERGE EVERYTHING
# =====================================================================
merged = solar_df.merge(wind_df, on=["City","Year","Month"], how="left")
merged = merged.merge(sunshine, on=["City","Year","Month"], how="left")
merged = merged.merge(cloud, on=["City","Year","Month"], how="left")
merged = merged.merge(population, on=["City","Year"], how="left")
merged = merged.merge(energy, on=["City","Year"], how="left")

# =====================================================================
# 7. ADD WIND POWER DENSITY
# =====================================================================
if "WS10M" in merged.columns:
    merged["Wind_Power_Density"] = 0.5 * 1.225 * (pd.to_numeric(merged["WS10M"], errors="coerce")**3)
else:
    merged["Wind_Power_Density"] = np.nan

# =====================================================================
# 8. SAVE OUTPUT
# =====================================================================
out_path = os.path.join(os.getcwd(), "MASTER_DATASET.csv")
merged.to_csv(out_path, index=False)

print("\n🎉 MASTER_DATASET CREATED SUCCESSFULLY!")
print("Rows:", len(merged))
print("Columns:", len(merged.columns))
print("Saved at:", out_path)
