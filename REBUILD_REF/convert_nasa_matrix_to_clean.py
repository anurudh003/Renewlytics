import pandas as pd
import os

# ======================================================
# CONFIGURATION (CHANGE ONLY THIS)
# ======================================================
INPUT_PATH = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\data"
OUTPUT_FOLDER = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\cleaned"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ======================================================
# FUNCTION TO CONVERT ONE NASA MATRIX FILE
# ======================================================
def convert_nasa_matrix(file_path, output_path):

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    header_line = None
    for i, line in enumerate(lines):
        cleaned = line.strip().upper()
        if cleaned.startswith("PARAM") and "YEAR" in cleaned and "JAN" in cleaned:
            header_line = i
            break

    if header_line is None:
        print(f"❌ Skipping (header not found): {os.path.basename(file_path)}")
        return

    df = pd.read_csv(
        file_path,
        skiprows=header_line,
        sep=r"\s+|,",
        engine="python"
    )

    expected_cols = [
        "PARAM", "YEAR",
        "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
        "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "ANN"
    ]

    df = df.iloc[:, :len(expected_cols)]
    df.columns = expected_cols

    df = df[pd.to_numeric(df["YEAR"], errors="coerce").notna()]
    df["YEAR"] = df["YEAR"].astype(int)

    df_long = df.melt(
        id_vars=["PARAM", "YEAR"],
        value_vars=expected_cols[2:-1],
        var_name="MONTH",
        value_name="VALUE"
    )

    month_map = {
        "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
        "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
        "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
    }

    df_long["MONTH_NUM"] = df_long["MONTH"].map(month_map)

    df_long["DATE"] = pd.to_datetime(
        dict(
            year=df_long["YEAR"],
            month=df_long["MONTH_NUM"],
            day=1
        )
    )

    clean_df = (
        df_long[["DATE", "PARAM", "VALUE"]]
        .sort_values("DATE")
        .reset_index(drop=True)
    )

    clean_df.to_csv(output_path, index=False)
    print(f"✅ Converted: {os.path.basename(file_path)}")


# ======================================================
# MAIN LOGIC — AUTO-DETECT FILE OR FOLDER
# ======================================================
if os.path.isfile(INPUT_PATH):

    # SINGLE FILE MODE
    if INPUT_PATH.lower().endswith("_clean.csv"):
        print("⚠️ File already cleaned. Skipping.")
    else:
        output_file = os.path.basename(INPUT_PATH).replace(".csv", "_clean.csv")
        output_path = os.path.join(OUTPUT_FOLDER, output_file)
        convert_nasa_matrix(INPUT_PATH, output_path)

elif os.path.isdir(INPUT_PATH):

    # FOLDER MODE
    for filename in os.listdir(INPUT_PATH):

        if not filename.lower().endswith(".csv"):
            continue

        if filename.lower().endswith("_clean.csv"):
            continue

        input_file = os.path.join(INPUT_PATH, filename)
        output_file = filename.replace(".csv", "_clean.csv")
        output_path = os.path.join(OUTPUT_FOLDER, output_file)

        convert_nasa_matrix(input_file, output_path)

else:
    raise Exception("❌ INPUT_PATH is neither a file nor a directory")

print("\n🎯 Processing completed successfully.")
