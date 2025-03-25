import pandas as pd
import unicodedata
import re

pd.set_option('display.max_columns', None)
lebron_df = pd.read_excel('../../data/Lebron.xlsx')
box_score = pd.read_excel('../../data/boxscore_2023.xlsx')

print(f"LEBRON Dataset Shape: {lebron_df.shape}")
print("\nColumn Names:")
print(lebron_df.columns.tolist())


print("\nChecking for duplicate player-season combinations:")

if 'Player' in lebron_df.columns and 'Season' in lebron_df.columns:
    duplicates = lebron_df.duplicated(subset=['Player', 'Season'], keep=False)
    if duplicates.any():
        print(f"Found {duplicates.sum()} duplicate player-season combinations")
        print(lebron_df[duplicates].sort_values(['Player', 'Season']).head(10))
    else:
        print("No duplicate player-season combinations found")

def normalize_player_name(name):
    if not isinstance(name, str):
        return ""
    
    # Step 1: Lowercase and strip
    name = name.lower().strip()
    
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    
    name = re.sub(r'[.,]', '', name)
    name = re.sub(r'\b(sr|jr|ii|iii|iv)\b', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    name_mapping = {
        'guillermo hernangomez': 'willy hernangomez',
        'juan hernangomez': 'juancho hernangomez',
        'jonathan simmons': 'jonathon simmons',
        'sheldon mcclellan': 'sheldon mac',
        'walter tavares': 'edy tavares',
        'tim luwawu-cabarrot': 'timothe luwawu-cabarrot',
        'n nene': 'nene',
        'zhou': 'zhou qi',
        'charlie brown': 'charles brown',
        'didi louzada': 'marcos louzada silva',
        'nic claxton': 'nicolas claxton',
        'enes freedom': 'enes kanter',
        'bones hyland': "nah'shon hyland",
        'nate williams': 'jeenathan williams',
        'kj martin': 'kenyon martin'
    }

    if name in name_mapping:
        return name_mapping[name]
    return name

# Check for players with special characters in their names
special_char_pattern = re.compile(r'[^\x00-\x7F]')  # Matches non-ASCII characters

special_char_players = []
for player in lebron_df['Player']:
    if isinstance(player, str) and special_char_pattern.search(player):
        special_char_players.append(player)

if special_char_players:
    print("Players with special characters:")
    for player in sorted(set(special_char_players)):
        normalized = normalize_player_name(player)
        print(f"Original: {player} → Normalized: {normalized}")


lebron_df['player_name'] = lebron_df['Player'].apply(normalize_player_name)


changed_names = lebron_df[lebron_df['Player'].apply(lambda x: 
    isinstance(x, str) and normalize_player_name(x) != x.lower().strip())]

print(f"\nTotal players with name changes after normalization: {len(changed_names['Player'].unique())}")

print("\nSeason values in LEBRON dataset:")
print(lebron_df['Season'].unique())


if isinstance(lebron_df['Season'].iloc[0], str) and '-' in lebron_df['Season'].iloc[0]:
    # Convert "2015-16" format to end year (2016)
    lebron_df['season'] = lebron_df['Season'].apply(
        lambda x: int(x.split('-')[1]) + 2000 if isinstance(x, str) and '-' in x else x
    )
    print("\nConverted season format:")
    print(lebron_df[['Season', 'season']])
    lebron_df = lebron_df.drop(columns = ['Season'])
    print(sorted(lebron_df['season'].unique()))
    print(lebron_df.head())

lebron_df = lebron_df[lebron_df['season']<2025]
lebron_df = lebron_df.drop(columns=['Team(s)'])
print("DataFrame index info:", lebron_df.index)
# Select just the columns you need
cols_to_keep = ['player_name', 'season','LEBRON WAR' ,'LEBRON', 'O-LEBRON', 'D-LEBRON','Offensive Archetype','Defensive Role','Rotation Role']
# Add any other columns you need
lebron_df = lebron_df[cols_to_keep]
print(lebron_df.columns)
print(lebron_df.head())
lebron_df.to_excel('../../data/lebron_processed.xlsx', index=False)
# print(lebron_df.columns)
# print(lebron_df[55:58])
# lebron_df = lebron_df.drop(columns=['Season'])
# print(lebron_df.columns)
# def clean_name(name):
#     """Standardize player names by removing punctuation, suffixes, and handling special cases"""
#     if not isinstance(name, str):
#         return ""
    
#     # Convert to lowercase and strip whitespace
#     name = name.lower().strip()
    
#     # Remove common suffixes and punctuation
#     name = re.sub(r'[.,]', '', name)
#     name = re.sub(r'\b(sr|jr|ii|iii|iv)\b', '', name)
    
#     # Handle specific name variations (add any other mappings from your existing code)
#     name_mapping = {
#         'guillermo hernangomez': 'willy hernangomez',
#         'juan hernangomez': 'juancho hernangomez',
#         'jonathan simmons': 'jonathon simmons',
#         'sheldon mcclellan': 'sheldon mac',
#         'walter tavares': 'edy tavares',
#         'tim luwawu-cabarrot': 'timothe luwawu-cabarrot',
#         'n nene': 'nene',
#         'zhou': 'zhou qi',
#         'charlie brown': 'charles brown',
#         'didi louzada': 'marcos louzada silva',
#         'nic claxton': 'nicolas claxton',
#         'enes freedom': 'enes kanter',
#         'bones hyland':"nah'shon hyland",
#         'nate williams':'jeenathan williams',
#         'kj martin':'kenyon martin'
#     }
    
#     # Apply specific mappings if name is in the dictionary
#     if name in name_mapping:
#         return name_mapping[name]
    
#     # Final cleanup - remove extra spaces
#     return re.sub(r'\s+', ' ', name).strip()

# # Apply name cleaning if there's a 'Player' column
# if 'Player' in lebron_df.columns:
#     lebron_df['standardized_player_name'] = lebron_df['Player'].apply(clean_name)
    
#     # Check if cleaning affected uniqueness
#     print("\nUnique players before cleaning:", lebron_df['Player'].nunique())
#     print("Unique players after cleaning:", lebron_df['standardized_player_name'].nunique())
    
#     # Check for newly created duplicates after name standardization
#     new_duplicates = lebron_df.duplicated(subset=['standardized_player_name', 'Season'], keep=False)
#     if new_duplicates.any():
#         print(f"\nFound {new_duplicates.sum()} duplicate player-season combinations after name standardization")
#         print(lebron_df[new_duplicates].sort_values(['standardized_player_name', 'Season']).head(10))

# # Preview the processed data
# print("\nProcessed LEBRON data preview:")
# print(lebron_df.head())