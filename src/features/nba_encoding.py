import pandas as pd
import numpy as np
import os
import json
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

pd.set_option('display.max_columns', None)
df = pd.read_excel('../../data/feature_reduction/merged_2024.xlsx')
    

# if 'tm_id' in df.columns:
#     print(f"Number of unique team_ids: {df['tm_id'].nunique()}")
#     print("Sample team_ids:", df['tm_id'].unique()[:5]) 

# all_teams = sorted(list(set(df['team_name'].unique()).union(set(df['opponent_team'].unique()))))
# team_mapping = {team: idx for idx, team in enumerate(all_teams)}
# print(team_mapping)
# df['team_id'] = df['team_name'].map(team_mapping)
# df['opponent_id'] = df['opponent_team'].map(team_mapping)
# mapping_file = '../../data/team_id_mapping.json'
# os.makedirs(os.path.dirname(mapping_file), exist_ok=True)
# with open(mapping_file, 'w') as f:
#     json.dump(team_mapping, f)

# print(f"Created and saved mapping for {len(team_mapping)} teams to {mapping_file}")

with open('../../data/team_id_mapping.json', 'r') as f:
    team_mapping = json.load(f)

df['team_id'] = df['team_name'].map(team_mapping)
df['opponent_id'] = df['opponent_team'].map(team_mapping)
df = df.drop(columns=['team_name','opponent_team','season','player_name'])

df.rename(columns={'VENUE\n(R/H/N)': 'venue(R/H)'}, inplace=True)

binary_features = {
    'venue(R/H)': {'R': 0, 'H': 1, 'N': 0},
    'starter(Y/N)': {'N': 0, 'Y': 1}
}
for col, mapping in binary_features.items():
    if col in df.columns:
        df[f"{col.split('(')[0]}_binary"] = df[col].map(mapping)
        print(f"Binary encoded {col} → {col.split('(')[0]}_binary")
df = df.drop(columns=['venue(R/H)','starter(Y/N)'])


if 'position' in df.columns:
    unique_positions = df['position'].unique()
    print(f"Unique positions: {unique_positions}")
    print(f"Number of unique positions: {len(unique_positions)}")

# Unique positions: ['F' 'C' 'G-F' 'G' 'F-C' 'C-F' 'F-G']
# Need to handle players who play multiple positions on the court so I broke down the positions into 3 base categories to encode 
df['is_G'] = df['position'].str.contains('G').astype(int)
df['is_F'] = df['position'].str.contains('F').astype(int)
df['is_C'] = df['position'].str.contains('C').astype(int)

df = df.drop(columns=['position'])

# if 'rest_days' in df.columns:
#     unique_rest_days = df['rest_days'].unique()
#     print(f"Unique rest days values: {unique_rest_days}")
#     value_counts = df['rest_days'].value_counts()
#     print("Value counts:")
#     print(value_counts)

"""
Now I have an issue with rest days. I dont want the model to confuse rest days and
injuries so I am going to set a threshold of 9 days rest as actual rest and then 
anything over 9 days will have a binary flag that says the player was injured
"""
if 'rest_days' in df.columns:
    # Convert '3+' to 3
    df['rest_days_numeric'] = df['rest_days'].replace('3+', 3).astype(float)
    
    df['extended_absence'] = (df['rest_days_numeric'] > 9).astype(int)
    
    df = df.drop(columns=['rest_days'])

"""Now its time to embedd the offensive archetypes so the TFT can learn from this """
# if 'Offensive Archetype' in df.columns:
#     offensive_encoder = LabelEncoder()
#     offensive_encoder.fit(df['Offensive Archetype'])
#     offensive_mapping = dict(zip(offensive_encoder.classes_, range(len(offensive_encoder.classes_))))
#     os.makedirs(os.path.dirname('../../data/offensive_archetype_mapping.json'), exist_ok=True)
#     with open('../../data/offensive_archetype_mapping.json', 'w') as f:
#         json.dump(offensive_mapping, f)
    
#     print(f"Created and saved mapping for {len(offensive_mapping)} offensive archetypes")
#     print("Mapping:", offensive_mapping)

with open('../../data/offensive_archetype_mapping.json', 'r') as f:
    offensive_mapping = json.load(f)

if 'Offensive Archetype' in df.columns:
    df['offensive_archetype_id'] = df['Offensive Archetype'].map(offensive_mapping)
    
    df = df.drop(columns=['Offensive Archetype'])
    
    print(f"Applied offensive archetype mapping from file")

if 'Defensive Role' in df.columns:
    unique_roles = df['Defensive Role'].unique()
    print(f"Unique Defensive Roles: {unique_roles}")
    print(f"Number of unique roles: {len(unique_roles)}")
    
    # Optional: See the distribution
    role_counts = df['Defensive Role'].value_counts()
    print("\nDefensive Role distribution:")
    print(role_counts)

"""NOw For Defensive Embedding"""
# if 'Defensive Role' in df.columns:
#     # Create label encoder
#     defensive_encoder = LabelEncoder()
    
#     # Fit encoder to get the classes
#     defensive_encoder.fit(df['Defensive Role'])
    
#     # Create mapping from encoder
#     defensive_mapping = dict(zip(defensive_encoder.classes_, range(len(defensive_encoder.classes_))))
    
#     os.makedirs(os.path.dirname('../../data/defensive_role_mapping.json'), exist_ok=True)
#     with open('../../data/defensive_role_mapping.json', 'w') as f:
#         json.dump(defensive_mapping, f)
    
#     print(f"Created and saved mapping for {len(defensive_mapping)} defensive roles")
#     print("Mapping:", defensive_mapping)


with open('../../data/defensive_role_mapping.json', 'r') as f:
    defensive_mapping = json.load(f)

if 'Defensive Role' in df.columns:

    df['defensive_role_id'] = df['Defensive Role'].map(defensive_mapping)
    
    df = df.drop(columns=['Defensive Role'])
    
    print(f"Applied defensive role mapping from file")

print(df.head())

# if 'Rotation Role' in df.columns:
#     # Create label encoder
#     rotation_encoder = LabelEncoder()
    
#     # Fit encoder to get the classes
#     rotation_encoder.fit(df['Rotation Role'])
    
#     # Create mapping from encoder
#     rotation_mapping = dict(zip(rotation_encoder.classes_, range(len(rotation_encoder.classes_))))
    
#     os.makedirs(os.path.dirname('../../data/rotation_role_mapping.json'), exist_ok=True)
#     with open('../../data/rotation_role_mapping.json', 'w') as f:
#         json.dump(rotation_mapping, f)
    
#     print(f"Created and saved mapping for {len(rotation_mapping)} rotation roles")
#     print("Mapping:", rotation_mapping)

if 'Rotation Role' in df.columns:
    # Load the existing rotation role mapping
    with open('../../data/rotation_role_mapping.json', 'r') as f:
        rotation_mapping = json.load(f)

    # Process all unique rotation roles in the dataframe
    unique_roles = df['Rotation Role'].unique()
    for role in unique_roles:
        if role not in rotation_mapping:
            new_val = max(rotation_mapping.values()) + 1 if rotation_mapping else 0
            rotation_mapping[role] = new_val

    # Save the updated mapping back to the JSON file
    with open('../../data/rotation_role_mapping.json', 'w') as f:
        json.dump(rotation_mapping, f)

    # Apply the updated mapping to the dataframe
    df['rotation_role_id'] = df['Rotation Role'].map(rotation_mapping)
    df = df.drop(columns=['Rotation Role'])
    print("Applied updated rotation role mapping from file")



categorical_columns = [
    'player_id', 'team_id','opponent_id', 'offensive_archetype_id','defensive_role_id','rotation_role_id'
]
for col in categorical_columns:
    df[col] = df[col].astype('category')

if 'tm_id' in df.columns:
    df = df.drop(columns=['tm_id'])


print(df.info())
df.to_excel('../../data/final_final_data/final_final_2024.xlsx')
print("2024")