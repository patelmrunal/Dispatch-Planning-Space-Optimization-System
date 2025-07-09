#!/usr/bin/env python3
"""
train_ai.py
Standalone script to train the AI models on historical optimization data.
Run this script to improve the AI's accuracy based on saved job data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.ai_trainer import AITrainer
from utils.job_db import list_jobs, get_job_by_id
import json

def main():
    print("🤖 AI Training for Dispatch Optimization System")
    print("=" * 50)
    
    # Initialize trainer
    trainer = AITrainer()
    
    # Load historical jobs
    print("📊 Loading historical optimization jobs...")
    jobs = list_jobs()
    
    if len(jobs) < 10:
        print(f"❌ Not enough data! Found {len(jobs)} jobs, need at least 10 for training.")
        print("💡 Run more optimizations to collect training data.")
        return
    
    print(f"✅ Found {len(jobs)} historical jobs")
    
    # Get full job data
    historical_data = []
    for job_id, timestamp in jobs:
        job_data = get_job_by_id(job_id)
        if job_data:
            historical_data.append(job_data)
    
    print(f"📈 Preparing training data from {len(historical_data)} jobs...")
    
    # Train the models
    print("🧠 Training AI models...")
    success = trainer.train(historical_data)
    
    if success:
        print("✅ Training completed successfully!")
        
        # Save models
        print("💾 Saving trained models...")
        if trainer.save_models():
            print("✅ Models saved to models/trained_models/")
        else:
            print("❌ Failed to save models")
        
        # Test prediction on a sample
        print("\n🧪 Testing predictions...")
        if len(historical_data) > 0:
            sample_job = historical_data[0]
            input_data = sample_job[2]  # input_csv
            constraints = json.loads(sample_job[3])  # constraints
            
            # Parse sample data
            import pandas as pd
            import io
            df = pd.read_csv(io.StringIO(input_data))
            products = df.to_dict(orient='records')
            
            prediction = trainer.predict_optimization_quality(products, constraints)
            if "error" not in prediction:
                print(f"📊 Sample prediction:")
                print(f"   Predicted trucks needed: {prediction['predicted_trucks']}")
                print(f"   Optimization confidence: {prediction['optimization_confidence']:.2%}")
                if prediction['recommendations']:
                    print(f"   Recommendations: {', '.join(prediction['recommendations'])}")
        
        print("\n🎉 AI training complete! The system will now provide more accurate predictions.")
        print("💡 Run this script again after collecting more data to retrain the models.")
        
    else:
        print("❌ Training failed!")

if __name__ == "__main__":
    main() 