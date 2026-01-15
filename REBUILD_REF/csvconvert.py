import rasterio
import pandas as pd

# ------------------------------
# 1. Your uploaded WorldPop file
# ------------------------------
tif_file = r"C:\Users\anuru\Downloads\ind_pop_2020_CN_1km_R2025A_UA_v1.tif"  # <-- put correct file path

# ------------------------------------
# 2. Your 15 cities with lat/lon
# ------------------------------------
cities = [
    ("Delhi", 28.7041, 77.1025),
    ("Mumbai", 19.0760, 72.8777),
    ("Chennai", 13.0827, 80.2707),
    ("Bengaluru", 12.9716, 77.5946),
    ("Hyderabad", 17.3850, 78.4867),
    ("Kolkata", 22.5726, 88.3639),
    ("Jaipur", 26.9124, 75.7873),
    ("Ahmedabad", 23.0225, 72.5714),
    ("Pune", 18.5204, 73.8567),
    ("Kochi", 9.9312, 76.2673),
    ("Lucknow", 26.8467, 80.9462),
    ("Gandhinagar", 23.2237, 72.6500),
    ("Bhopal", 23.2599, 77.4126),
    ("Raipur", 21.2514, 81.6296),
    ("Guwahati", 26.1445, 91.7362)
]

# ---------------------------------------------------
# 3. Read the raster and extract population per city
# ---------------------------------------------------
pop_data = []

with rasterio.open(tif_file) as src:
    for city, lat, lon in cities:
        # Convert lat/lon → raster row/col
        row, col = src.index(lon, lat)

        # Extract pixel value (population count)
        pop_2020 = src.read(1)[row, col]

        pop_data.append([city, lat, lon, int(pop_2020)])

# --------------------------------------
# 4. Convert to CSV
# --------------------------------------
df = pd.DataFrame(pop_data, columns=["City", "Latitude", "Longitude", "Population_2020"])

df.to_csv("population_2020_extracted.csv", index=False)

print("CSV saved as population_2020_extracted.csv")
