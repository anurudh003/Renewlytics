import pandas as pd
import glob
import os
import re
import numpy as np

# -----------------------------------------------------------
# 1️⃣  SET YOUR DATA DIRECTORY
# -----------------------------------------------------------
DATA_DIR = "./data"   # Make sure all CSVs are inside this folder

# -----------------------------------------------------------
# 2️⃣  LIST OF YOUR 15 CITIES
# -----------------------------------------------------------
cities = [
    "Delhi","Mumbai","Chennai","Bengaluru","Hyderabad","Kolkata","Jaipur",
    "Ahmedabad","Pune","Kochi","Lucknow","Gandhinagar","Bhopal","Raipur","Guwahati"
]

# -----------------------------------------------------------
# 3️⃣  LOAD OTHER DATASETS
# -----------------------------------------------------------
print("\n📌 Loading sunshine/cloud/population/energy datasets...\n")

sunshine = pd.read_csv(f"{DATA_DIR}/sunshine_india_2015_2024.csv")
cloud = pd.read_csv(f"{DATA_DIR}/cloudcover_india_2015_2024.csv")
population = pd.read_csv(f"{DATA_DIR}/final_population_2015_2024.csv")
energy = pd.read_csv(f"{DATA_DIR}/city_energy_2015_2024.csv")

# Standardize column names
sunshine.columns = ["City","Year","Month","Sunshine_Hours"]
cloud.columns = ["City","Year","Month","Cloud_Cover"]
population.columns = ["City","Year","Population","Population_Density","Growth_Rate"]
energy.columns = ["City","State","Year","Energy_Consumption_GWh","Per_Capita_kWh","Peak_Demand_MW"]

# -----------------------------------------------------------
# 4️⃣  LOAD SOLAR + WIND NASA FILES WITH DEBUGGING
# -----------------------------------------------------------
solar_frames = []
wind_frames = []

print("\n🔍 Checking files inside:", DATA_DIR)
print("-------------------------------------------")

for city in cities:
    solar_path = f"{DATA_DIR}/{city}_solar.csv"
    wind_path = f"{DATA_DIR}/{city}_wind.csv"

    # SOLAR FILE
    if os.path.exists(solar_path):
        print(f"✔ Found solar file: {city}_solar.csv")
        df_solar = pd.read_csv(solar_path)
        df_solar["City"] = city
        solar_frames.append(df_solar)
    else:
        print(f"❌ Missing solar file: {city}_solar.csv")

    # WIND FILE
    if os.path.exists(wind_path):
        print(f"✔ Found wind file: {city}_wind.csv")
        df_wind = pd.read_csv(wind_path)
        df_wind["City"] = city
        wind_frames.append(df_wind)
    else:
        print(f"❌ Missing wind file: {city}_wind.csv")

# STOP IF NO SOLAR FILES FOUND
if len(solar_frames) == 0:
    raise Exception("\n🚫 ERROR: No solar files found.\n→ Check filenames\n→ Check file paths\n→ Check city names\n")

solar_df = pd.concat(solar_frames, ignore_index=True)

# STOP IF NO WIND FILES FOUND
if len(wind_frames) == 0:
    raise Exception("\n🚫 ERROR: No wind files found.\n→ Check filenames\n→ Check file paths\n→ Check city names\n")

wind_df = pd.concat(wind_frames, ignore_index=True)

# -----------------------------------------------------------
# 5️⃣  CLEAN SOLAR + WIND DATA (Extract Year/Month)
# -----------------------------------------------------------
solar_df["Year"] = solar_df["YEAR"]
solar_df["Month"] = solar_df["MO"]

wind_df["Year"] = wind_df["YEAR"]
wind_df["Month"] = wind_df["MO"]

solar_cols = [
    "City","Year","Month",
    "ALLSKY_SFC_SW_DWN","ALLSKY_SFC_SW_DNI","ALLSKY_SFC_SW_DIFF",
    "T2M","T2M_MAX","T2M_MIN","RH2M","CLD_FRAC","PS"
]

wind_cols = ["City","Year","Month","WS2M","WS10M","WD10M"]

solar_df = solar_df[[c for c in solar_cols if c in solar_df.columns]]
wind_df = wind_df[[c for c in wind_cols if c in wind_df.columns]]

# -----------------------------------------------------------
# 6️⃣  MERGE SOLAR + WIND
# -----------------------------------------------------------
merged = solar_df.merge(wind_df, on=["City","Year","Month"], how="left")

# -----------------------------------------------------------
# 7️⃣  MERGE WITH OTHER DATASETS
# -----------------------------------------------------------
merged = merged.merge(sunshine, on=["City","Year","Month"], how="left")
merged = merged.merge(cloud, on=["City","Year","Month"], how="left")
merged = merged.merge(population, on=["City","Year"], how="left")
merged = merged.merge(energy, on=["City","Year"], how="left")

# -----------------------------------------------------------
# 8️⃣  ADD WIND POWER DENSITY (W/m²)
# -----------------------------------------------------------
AIR_DENSITY = 1.225
if "WS10M" in merged.columns:
    merged["Wind_Power_Density"] = 0.5 * AIR_DENSITY * (merged["WS10M"] ** 3)
else:
    merged["Wind_Power_Density"] = np.nan

# -----------------------------------------------------------
# 9️⃣  SAVE FINAL MASTER DATASET
# -------------
