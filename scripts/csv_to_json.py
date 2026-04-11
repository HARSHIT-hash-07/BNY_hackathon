
import pandas as pd
import json
import os

def convert_to_json():
    csv_path = 'output/kyc_output.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    
    # Clean data for JSON
    data = df.to_dict(orient='records')
    
    frontend_data_path = 'frontend/src/data/kyc_data.json'
    os.makedirs(os.path.dirname(frontend_data_path), exist_ok=True)
    
    with open(frontend_data_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Successfully converted {len(data)} records to {frontend_data_path}")

if __name__ == "__main__":
    convert_to_json()
