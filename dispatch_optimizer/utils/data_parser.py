"""
data_parser.py
Reads and cleans input CSV data for dispatch planning.
"""

import pandas as pd
from datetime import datetime

def parse_product_csv(file):
    """
    Parse the product CSV file into a list of product dicts.
    Args:
        file (str or file-like): Path to the CSV file or file-like object.
    Returns:
        list of dict: Parsed product data.
    """
    df = pd.read_csv(file)
    # Clean and convert data types
    df['Weight'] = df['Weight'].astype(float)
    df['Length'] = df['Length'].astype(float)
    df['Width'] = df['Width'].astype(float)
    df['Height'] = df['Height'].astype(float)
    df['Fragile'] = df['Fragile'].map(lambda x: str(x).strip().lower() in ['yes', 'y', 'true', '1'])
    df['DispatchDate'] = pd.to_datetime(df['DispatchDate'], errors='coerce')
    # Strip whitespace from string columns
    df['Product'] = df['Product'].astype(str).str.strip()
    df['Destination'] = df['Destination'].astype(str).str.strip()
    df['Priority'] = df['Priority'].astype(str).str.strip()
    # Convert to list of dicts
    return df.to_dict(orient='records') 