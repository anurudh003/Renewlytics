import pandas as pd
import os

# ======================================================
# STEP 1: ABSOLUTE PATHS (FIXES FILE ERRORS)
# ======================================================
HISTORICAL_PATH = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\master\india_renewable_energy_analytics_master.csv"
FORECAST_PATH = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\renewable_energy_forecast_till_2034.csv"

# ======================================================
# STEP 2: LOAD DATA
# ======================================================
historical_df = pd.read_csv(HISTORICAL_PATH)
forecast_df = pd.read_csv(FORECAST_PATH)

print("✅ Datasets loaded")

# ======================================================
# STEP 3: STANDARDIZE COMMON IDENTIFIERS
# ======================================================
historical_df.rename(columns={
    "date": "DATE",
    "city": "CITY"
}, inplace=True)

forecast_df.rename(columns={
    "DATE": "DATE",
    "CITY": "CITY"
}, inplace=True)

historical_df["DATE"] = pd.to_datetime(historical_df["DATE"])
forecast_df["DATE"] = pd.to_datetime(forecast_df["DATE"])

# ======================================================
# STEP 4: ADD DATA TYPE FLAG
# ======================================================
historical_df["DATA_TYPE"] = "Actual"
forecast_df["DATA_TYPE"] = "Forecast"

# ======================================================
# STEP 5: ALIGN COLUMNS WITHOUT DROPPING ANY
# ======================================================
# Union of all columns
all_columns = sorted(
    set(historical_df.columns).union(set(forecast_df.columns))
)

historical_df = historical_df.reindex(columns=all_columns)
forecast_df = forecast_df.reindex(columns=all_columns)

# ======================================================
# STEP 6: COMBINE DATASETS
# ======================================================
combined_df = pd.concat(
    [historical_df, forecast_df],
    ignore_index=True
)

combined_df = combined_df.sort_values(
    ["CITY", "DATE"]
).reset_index(drop=True)

# ======================================================
# STEP 7: SAVE FINAL STREAMLIT DATASET
# ======================================================
OUTPUT_PATH = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\renewable_energy_full_actual_and_forecast.csv"

combined_df.to_csv(OUTPUT_PATH, index=False)

print("\n✅ Full combined dataset created")
print(f"📁 Saved at: {OUTPUT_PATH}")

# ======================================================
# STEP 8: SANITY CHECK
# ======================================================
print("\n📊 Columns retained:")
print(list(combined_df.columns))

print("\n📅 Year range:")
print(
    combined_df["DATE"].dt.year.min(),
    "→",
    combined_df["DATE"].dt.year.max()
)

print("\n📈 Data type distribution:")
print(combined_df["DATA_TYPE"].value_counts())
