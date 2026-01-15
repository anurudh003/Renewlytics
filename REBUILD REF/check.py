import os

# Define path to one of the messy files
file_path = './data/Ahmedabad_solar.csv'

print(f"--- RAW FILE INSPECTOR: {os.path.basename(file_path)} ---")

if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        # Read the first 20 lines
        for i in range(20):
            line = f.readline().strip()
            print(f"Row {i}: {line}")
else:
    print("❌ File not found. Check path.")