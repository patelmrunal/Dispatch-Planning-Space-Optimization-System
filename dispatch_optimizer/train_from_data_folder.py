import os
import json
import pandas as pd
from models.ai_trainer import AITrainer

# Path to data folder
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Dummy constraints
default_constraints = {
    "max_truck_weight": 1000,
    "max_truck_volume": 10000,
    "fragile_on_top": True,
    "priority_first": True
}

def main():
    print("🤖 Training AI model from all CSVs in data/ folder...")
    trainer = AITrainer()
    job_tuples = []

    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.csv'):
            file_path = os.path.join(DATA_DIR, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                input_csv = f.read()
            # Use input as dummy output
            output_csv = input_csv
            constraints_json = json.dumps(default_constraints)
            # Tuple: (id, timestamp, input_csv, constraints, output_csv)
            job_tuples.append((None, None, input_csv, constraints_json, output_csv))

    print(f"Found {len(job_tuples)} CSV files for training.")
    if len(job_tuples) < 10:
        print("❌ Not enough data for training (need at least 10 CSVs). Aborting.")
        return

    print("🧠 Training model...")
    success = trainer.train(job_tuples)
    if success:
        print("✅ Training completed successfully!")
        if trainer.save_models():
            print("💾 Models saved to models/trained_models/")
        else:
            print("❌ Failed to save models.")
    else:
        print("❌ Training failed!")

if __name__ == "__main__":
    main() 