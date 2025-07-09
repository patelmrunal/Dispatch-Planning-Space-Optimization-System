"""
demand_predictor.py
Placeholder for ML-based demand forecasting (optional, for future use).
"""

import pandas as pd

def predict_demand(product_history):
    """
    Predict future demand for products using a moving average.
    Args:
        product_history (list of dict): Historical product data with 'Product' and 'Quantity' columns.
    Returns:
        dict: Predicted demand per product.
    """
    df = pd.DataFrame(product_history)
    if 'Product' not in df or 'Quantity' not in df:
        return {}
    # Group by product and take mean quantity as prediction
    demand = df.groupby('Product')['Quantity'].mean().to_dict()
    return demand 