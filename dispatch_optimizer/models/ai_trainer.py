"""
ai_trainer.py
Machine learning module to train the AI system on historical optimization data.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
import io
import json

class AITrainer:
    def __init__(self):
        self.weight_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.volume_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.truck_count_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.optimization_improver = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_training_data(self, historical_jobs):
        """
        Prepare training data from historical optimization jobs.
        Args:
            historical_jobs (list): List of job data from database
        Returns:
            tuple: (X_features, y_targets)
        """
        features = []
        targets = []
        
        for job in historical_jobs:
            # Parse job data
            input_data = pd.read_csv(io.StringIO(job[2]))  # input_csv
            constraints = json.loads(job[3])  # constraints
            output_data = pd.read_csv(io.StringIO(job[4]))  # output_csv
            
            # Extract features
            total_weight = input_data['Weight'].sum()
            total_volume = (input_data['Length'] * input_data['Width'] * input_data['Height']).sum()
            num_products = len(input_data)
            avg_weight = input_data['Weight'].mean()
            avg_volume = (input_data['Length'] * input_data['Width'] * input_data['Height']).mean()
            fragile_count = (input_data['Fragile'] == 'Yes').sum()
            high_priority_count = (input_data['Priority'] == 'High').sum()
            
            # Extract targets from output
            trucks_used = output_data['Truck #'].max() if 'Truck #' in output_data.columns else 1
            total_dispatch_time = len(output_data)  # Simplified metric
            
            # Create feature vector
            feature_vector = [
                total_weight, total_volume, num_products, avg_weight, avg_volume,
                fragile_count, high_priority_count,
                constraints.get('max_truck_weight', 1000),
                constraints.get('max_truck_volume', 10000),
                constraints.get('fragile_on_top', True),
                constraints.get('priority_first', True)
            ]
            
            features.append(feature_vector)
            targets.append([trucks_used, total_dispatch_time])
        
        return np.array(features), np.array(targets)
    
    def train(self, historical_jobs):
        """
        Train the AI models on historical data.
        Args:
            historical_jobs (list): Historical job data from database
        """
        if len(historical_jobs) < 10:
            print("Need at least 10 historical jobs for training")
            return False
            
        X, y = self.prepare_training_data(historical_jobs)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train models
        self.truck_count_predictor.fit(X_train_scaled, y_train[:, 0])
        self.optimization_improver.fit(X_train_scaled, y_train[:, 0])
        
        # Evaluate
        train_score = self.truck_count_predictor.score(X_train_scaled, y_train[:, 0])
        test_score = self.truck_count_predictor.score(X_test_scaled, y_test[:, 0])
        
        print(f"Training completed! Train score: {train_score:.3f}, Test score: {test_score:.3f}")
        
        self.is_trained = True
        return True
    
    def predict_optimization_quality(self, products, constraints):
        """
        Predict how well the optimization will perform.
        Args:
            products (list): Product data
            constraints (dict): Optimization constraints
        Returns:
            dict: Predictions and recommendations
        """
        if not self.is_trained:
            return {"error": "Model not trained yet"}
        
        # Prepare features
        df = pd.DataFrame(products)
        total_weight = df['Weight'].sum()
        total_volume = (df['Length'] * df['Width'] * df['Height']).sum()
        num_products = len(df)
        avg_weight = df['Weight'].mean()
        avg_volume = (df['Length'] * df['Width'] * df['Height']).mean()
        fragile_count = (df['Fragile'] == True).sum()
        high_priority_count = (df['Priority'] == 'High').sum()
        
        features = [
            total_weight, total_volume, num_products, avg_weight, avg_volume,
            fragile_count, high_priority_count,
            constraints.get('max_truck_weight', 1000),
            constraints.get('max_truck_volume', 10000),
            constraints.get('fragile_on_top', True),
            constraints.get('priority_first', True)
        ]
        
        features_scaled = self.scaler.transform([features])
        
        predicted_trucks = self.truck_count_predictor.predict(features_scaled)[0]
        optimization_confidence = self.optimization_improver.predict_proba(features_scaled)[0]
        
        return {
            "predicted_trucks": int(predicted_trucks),
            "optimization_confidence": float(max(optimization_confidence)),
            "recommendations": self._generate_recommendations(features)
        }
    
    def _generate_recommendations(self, features):
        """Generate optimization recommendations based on features."""
        recommendations = []
        
        if features[0] > features[7] * 0.8:  # Total weight > 80% of max truck weight
            recommendations.append("Consider reducing max truck weight or splitting into smaller batches")
        
        if features[1] > features[8] * 0.8:  # Total volume > 80% of max truck volume
            recommendations.append("Consider reducing max truck volume or optimizing packaging")
        
        if features[5] > features[2] * 0.3:  # Fragile items > 30% of total
            recommendations.append("High fragile item count - ensure proper handling rules")
        
        return recommendations
    
    def save_models(self, path="models/trained_models"):
        """Save trained models to disk."""
        if not self.is_trained:
            return False
            
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.truck_count_predictor, f"{path}/truck_predictor.pkl")
        joblib.dump(self.optimization_improver, f"{path}/optimization_improver.pkl")
        joblib.dump(self.scaler, f"{path}/scaler.pkl")
        return True
    
    def load_models(self, path="models/trained_models"):
        """Load trained models from disk."""
        try:
            self.truck_count_predictor = joblib.load(f"{path}/truck_predictor.pkl")
            self.optimization_improver = joblib.load(f"{path}/optimization_improver.pkl")
            self.scaler = joblib.load(f"{path}/scaler.pkl")
            self.is_trained = True
            return True
        except:
            return False 