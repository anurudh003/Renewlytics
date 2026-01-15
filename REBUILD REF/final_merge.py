import pandas as pd
import glob
import os
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# CONFIGURATION
DATA_FOLDER = './data'
OUTPUT_FILE = 'Master_Dataset_Final.csv'

# Month mapping for date conversion
month_map = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
}

def process_nasa_files():
    print("--- STEP 1: PROCESSING SOLAR & WIND FILES ---")
    
    # Get all solar and wind files
    files = glob.glob(os.path.join(DATA_FOLDER, "*_solar.csv")) + \
            glob.glob(os.path.join(DATA_FOLDER, "*_wind.csv"))
    
    all_data = []

    for file in files:
        filename = os.path.basename(file)
        city = filename.split('_')[0] # Extract "Ahmedabad" from "Ahmedabad_solar.csv"
        
        try:
            # 1. READ: Skip the first 15 rows of metadata
            df = pd.read_csv(file, skiprows=15)
            
            # 2. CLEAN: Drop the 'ANN' (Annual) column if it exists
            if 'ANN' in df.columns:
                df = df.drop(columns=['ANN'])
            
            # 3. MELT: Convert Wide (Jan, Feb...) to Long (Month rows)
            # We keep PARAMETER and YEAR fixed, and melt the month columns
            df_melted = df.melt(id_vars=['PARAMETER', 'YEAR'], 
                                var_name='Month_Name', 
                                value_name='Value')
            
            # 4. FORMAT: Convert Month Name to Number
            df_melted['Month'] = df_melted['Month_Name'].map(month_map)
            df_melted['City'] = city
            
            all_data.append(df_melted)
            print(f"✅ Processed: {filename}")
            
        except Exception as e:
            print(f"❌ Error in {filename}: {e}")

    # Combine all cities into one big list
    big_df = pd.concat(all_data, ignore_index=True)

    print("\n--- STEP 2: PIVOTING PARAMETERS ---")
    # Now we have rows like: "ALLSKY... | 2015 | 1 | 1.6099"
    # We want "ALLSKY..." to be a COLUMN.
    
    # Pivot logic: Index is (City, Year, Month), Columns are (PARAMETER), Values are (Value)
    pivot_df = big_df.pivot_table(index=['City', 'Year', 'Month'], 
                                  columns='PARAMETER', 
                                  values='Value').reset_index()
    
    # Create a proper DateTime column
    pivot_df['Date'] = pd.to_datetime(pivot_df[['Year', 'Month']].assign(DAY=1))
    
    print(f"Pivot Shape: {pivot_df.shape}")
    return pivot_df

def merge_secondary_data(main_df):
    print("\n--- STEP 3: MERGING SECONDARY DATA ---")
    
    # 1. Cloud Cover (Join on City, Year, Month)
    cc_path = os.path.join(DATA_FOLDER, 'cloudcover_india_2015_2024.csv')
    if os.path.exists(cc_path):
        cc_df = pd.read_csv(cc_path)
        # Ensure merge keys are same type
        main_df = pd.merge(main_df, cc_df, on=['City', 'Year', 'Month'], how='left')
        print(f"✅ Merged Cloud Cover")
    
    # 2. Population (Join on City, Year) - This data is annual, so it repeats for every month
    pop_path = os.path.join(DATA_FOLDER, 'final_population_2015_2024.csv')
    if os.path.exists(pop_path):
        pop_df = pd.read_csv(pop_path)
        main_df = pd.merge(main_df, pop_df, on=['City', 'Year'], how='left')
        print(f"✅ Merged Population")

    # 3. City Energy (Join on City, Year)
    energy_path = os.path.join(DATA_FOLDER, 'city_energy_2015_2024.csv')
    if os.path.exists(energy_path):
        en_df = pd.read_csv(energy_path)
        # Clean specific column issue if needed
        main_df = pd.merge(main_df, en_df, on=['City', 'Year'], how='left')
        print(f"✅ Merged Energy Data")
        
    return main_df

# --- EXECUTION ---
if __name__ == "__main__":
    # Run the Pipeline
    nasa_df = process_nasa_files()
    final_df = merge_secondary_data(nasa_df)
    
    # Clean up columns (move Date to front)
    cols = ['Date', 'City', 'Year', 'Month'] + [c for c in final_df.columns if c not in ['Date', 'City', 'Year', 'Month']]
    final_df = final_df[cols]
    
    # Save
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n🎉 SUCCESS! Master dataset saved to: {OUTPUT_FILE}")
    print(f"Final Shape: {final_df.shape}")
    print(f"Sample:\n{final_df.head(2)}")