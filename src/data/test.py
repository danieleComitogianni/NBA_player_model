import pandas as pd
data = pd.read_parquet('../../data/merged_data_for_model/merged_model_data_collab.parquet')
data[:10000].to_csv('../../data/10000sample.csv')
