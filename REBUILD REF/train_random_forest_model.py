import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

# ======================================================
# STEP 1: LOAD DATA
# ======================================================
DATA_PATH = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\master\india_renewable_energy_analytics_master.csv"

df = pd.read_csv(DATA_PATH)

# ======================================================
# STEP 2: STANDARDIZE COLUMN NAMES
# ======================================================
df.rename(columns={
    "date": "DATE",
    "city": "CITY",
    "energy_generated": "ENERGY_GENERATED",
    "energy_efficiency_index": "EFFICIENCY_INDEX",
    "sunshine_hours": "SUNSHINE_HOURS",
    "temperature": "TEMPERATURE",
    "wind_speed": "WIND_SPEED",
    "allsky_sfc_sw_dwn": "SOLAR_IRRADIANCE",
    "rh2m": "HUMIDITY"
}, inplace=True)

df["DATE"] = pd.to_datetime(df["DATE"])
df = df.sort_values(["CITY", "DATE"]).reset_index(drop=True)

print("✅ Dataset loaded and standardized")

# ======================================================
# STEP 3: CREATE LAG FEATURES (CRITICAL)
# ======================================================
df["ENERGY_LAG_1"] = df.groupby("CITY")["ENERGY_GENERATED"].shift(1)
df["ENERGY_LAG_12"] = df.groupby("CITY")["ENERGY_GENERATED"].shift(12)

df = df.dropna().reset_index(drop=True)

# ======================================================
# STEP 4: ENCODE CITY
# ======================================================
le = LabelEncoder()
df["CITY_ENCODED"] = le.fit_transform(df["CITY"])

# ======================================================
# STEP 5: FEATURE SET (EFFICIENCY DOMINANT)
# ======================================================
FEATURES = [
    "CITY_ENCODED",
    "EFFICIENCY_INDEX",
    "SUNSHINE_HOURS",
    "SOLAR_IRRADIANCE",
    "TEMPERATURE",
    "WIND_SPEED",
    "HUMIDITY",
    "ENERGY_LAG_1",
    "ENERGY_LAG_12"
]

TARGET = "ENERGY_GENERATED"

X = df[FEATURES]
y = df[TARGET]

# ======================================================
# STEP 6: TIME-BASED SPLIT
# ======================================================
split_index = int(len(df) * 0.8)

X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

# ======================================================
# STEP 7: TRAIN RANDOM FOREST
# ======================================================
model = RandomForestRegressor(
    n_estimators=400,
    max_depth=20,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ======================================================
# STEP 8: EVALUATION
# ======================================================
y_pred = model.predict(X_test)

print("\n📊 MODEL PERFORMANCE")
print(f"MAE  : {mean_absolute_error(y_test, y_pred):.3f}")
print(f"RMSE : {np.sqrt(mean_squared_error(y_test, y_pred)):.3f}")
print(f"R²   : {r2_score(y_test, y_pred):.3f}")

# ======================================================
# STEP 9: RECURSIVE FORECASTING TILL 2034
# ======================================================
future_dates = pd.date_range(
    start=df["DATE"].max() + pd.offsets.MonthBegin(1),
    end="2034-12-01",
    freq="MS"
)

future_rows = []

for city in df["CITY"].unique():
    city_df = df[df["CITY"] == city].copy()
    last_row = city_df.iloc[-1].copy()

    for date in future_dates:
        row = last_row.copy()
        row["DATE"] = date

        X_future = pd.DataFrame([row[FEATURES]], columns=FEATURES)
        prediction = model.predict(X_future)[0]


        row["ENERGY_GENERATED"] = prediction
        row["ENERGY_LAG_12"] = row["ENERGY_LAG_1"]
        row["ENERGY_LAG_1"] = prediction

        future_rows.append(row)
        last_row = row

future_df = pd.DataFrame(future_rows)

# ======================================================
# STEP 10: MERGE HISTORICAL + FUTURE
# ======================================================
final_df = pd.concat([
    df[["DATE", "CITY", "ENERGY_GENERATED"]],
    future_df[["DATE", "CITY", "ENERGY_GENERATED"]]
]).reset_index(drop=True)

# ======================================================
# STEP 11: SAVE OUTPUT
# ======================================================
final_df.to_csv("renewable_energy_forecast_till_2034.csv", index=False)

print("\n✅ Renewable energy forecast generated till 2034 successfully.")
