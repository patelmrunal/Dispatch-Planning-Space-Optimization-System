import os
import pandas as pd

data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
threshold = 50
deleted = 0

for fname in os.listdir(data_dir):
    fpath = os.path.join(data_dir, fname)
    if fname.endswith('.csv'):
        try:
            n = len(pd.read_csv(fpath))
        except Exception as e:
            n = 0
        if n < threshold:
            os.remove(fpath)
            deleted += 1
            print(f'Deleted {fname} with {n} rows')
print(f'Total deleted: {deleted}') 