import pandas as pd
import os
from collections import defaultdict

# ======================================================
# CONFIGURATION (CHANGE PATHS IF NEEDED)
# ======================================================
CLEANED_FOLDER = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\cleaned"
FEATURE_FOLDER = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\features"
MASTER_FOLDER = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\master"

os.makedirs(FEATURE_FOLDER, exist_ok=True)
os.makedirs(MASTER_FOLDER, exist_ok=True)

# ======================================================
# STEP 1: GROUP FILES BY CITY
# ======================================================
city_files = defaultdict(dict)

for file in os.listdir(CLEANED_FOLDER):
    if not file.endswith("_clean.csv"):
        continue

    parts = file.replace("_clean.csv", "").split("_")
    city = parts[0]
    data_type = parts[1]   # solar or wind

    city_files[city][data_type] = os.path.join(CLEANED_FOLDER, file)

# ======================================================
# STEP 2: BUILD CITY-LEVEL FEATURE FILES
# ======================================================
all_cities_df = []

for city, files in city_files.items():

    dfs = []

    for dtype, path in files.items():
        df = pd.read_csv(path)

        # Pivot PARAM → columns
        pivot_df = df.pivot(index="DATE", columns="PARAM", values="VALUE")
        dfs.append(pivot_df)

    # Merge solar + wind on DATE
    city_df = pd.concat(dfs, axis=1)
    city_df = city_df.sort_index().reset_index()

    city_df["CITY"] = city

    # Save city-level feature file
    city_feature_path = os.path.join(FEATURE_FOLDER, f"{city}_features.csv")
    city_df.to_csv(city_feature_path, index=False)

    print(f"✅ Features created: {city}_features.csv")

    all_cities_df.append(city_df)

# ======================================================
# STEP 3: CREATE MASTER DATASET
# ======================================================
master_df = pd.concat(all_cities_df, ignore_index=True)
master_path = os.path.join(MASTER_FOLDER, "india_renewable_master.csv")
master_df.to_csv(master_path, index=False)

print("\n🎯 MASTER DATASET CREATED")
print(f"📄 Saved at: {master_path}")
print(master_df.head())
