import pandas as pd
import json
import os
import shutil

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

    # Copy generated SHAP plots to frontend assets folder automatically
    plots_src = 'output'
    plots_dest = 'frontend/public/plots'
    os.makedirs(plots_dest, exist_ok=True)
    
    plots_copied = 0
    for plot_name in ['shap_summary.png', 'shap_importance.png']:
        src_file = os.path.join(plots_src, plot_name)
        if os.path.exists(src_file):
            shutil.copy(src_file, os.path.join(plots_dest, plot_name))
            plots_copied += 1
            print(f"Copied {plot_name} -> {plots_dest}/{plot_name}")
            
    if plots_copied > 0:
        print(f"Successfully updated {plots_copied} SHAP plots in frontend asset folder.")

if __name__ == "__main__":
    convert_to_json()
