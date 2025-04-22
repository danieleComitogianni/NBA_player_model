import pandas as pd

pd.set_option('display.max_columns', None)
df = pd.read_excel('../../data/merged_data_for_model/merged_model_data.xlsx')

categorical_columns = [
    'player_id', 'team_id','opponent_id', 'offensive_archetype_id','defensive_role_id','rotation_role_id'
]
for col in categorical_columns:
    df[col] = df[col].astype('category')

dates_ordered = df['date'].is_monotonic_increasing
print("Dates are ordered:", dates_ordered)

df.to_parquet('../../data/merged_data_for_model/merged_model_data_collab_2.parquet')
