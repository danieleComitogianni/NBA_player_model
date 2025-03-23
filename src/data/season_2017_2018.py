import pandas as pd
import re

pd.set_option('display.max_columns', None)
darko_df = pd.read_excel('../../data/DARKO.xlsx')
box_score_2017 = pd.read_excel('../../data/boxscore_2017.xlsx')
lebron = pd.read_excel('../../data/lebron_processed.xlsx')
#OK i have the dataframe for darko, now I want to filter the dataframe so it removes every instance under 2014
filtered_darko_df = darko_df[darko_df['season']>=2015]
filtered_darko_df = filtered_darko_df[filtered_darko_df['season']<2025]

box_score_2017['DATE'] = pd.to_datetime(box_score_2017['DATE'])
box_score_2017.insert(3,'season',2018)

def clean_name(name):
    """
    Standardize player names by removing punctuation, suffixes, and handling special cases
    """
    if not isinstance(name, str):
        return ""
    
    # Convert to lowercase and strip whitespace
    name = name.lower().strip()
    
    # Remove common suffixes and punctuation
    name = re.sub(r'[.,]', '', name)
    name = re.sub(r'\b(sr|jr|ii|iii|iv)\b', '', name)
    
    # Handle specific name variations
    name_mapping = {
        'guillermo hernangomez': 'willy hernangomez',
        'juan hernangomez': 'juancho hernangomez',
        'jonathan simmons': 'jonathon simmons',
        'sheldon mcclellan': 'sheldon mac',
        'walter tavares': 'edy tavares',
        'tim luwawu-cabarrot': 'timothe luwawu-cabarrot',
        'n nene': 'nene',
        'zhou': 'zhou qi'
    }
    
    # Apply specific mappings if name is in the dictionary
    if name in name_mapping:
        return name_mapping[name]
    
    # Final cleanup - remove extra spaces
    return re.sub(r'\s+', ' ', name).strip()

box_score_2017 = box_score_2017.rename(columns={'OWN \nTEAM':'team_name','PLAYER \nFULL NAME': 'player_name', 'DAYS\nREST':'rest_days', 'STARTER\n(Y/N)': 'starter(y/n)','GAME-ID':'game_id','DATE':'date','PLAYER-ID':'player_id','POSITION':'position','OPPONENT \nTEAM':'opponent_team', 'VENUE\n(R/H)':'venue(R/H)','STARTER\n(Y/N)':'starter(Y/N)','USAGE \nRATE (%)':'usage_rate(%)'})
filtered_darko_df.drop(columns=['nba_id'], inplace=True)
filtered_darko_df.drop(columns=['team_name'], inplace=True)

box_score_2017['player_name'] = box_score_2017['player_name'].apply(clean_name)
filtered_darko_df['player_name'] = filtered_darko_df['player_name'].apply(clean_name)

merged_df_2017_2018 = pd.merge(box_score_2017,filtered_darko_df, on=['player_name','season'], how='left')
print(merged_df_2017_2018.info())
print(merged_df_2017_2018[:5])
print(merged_df_2017_2018.tail(5))

# Count rows with missing DARKO metrics
darko_cols = ['age', 'tm_id', 'dpm', 'o_dpm', 'd_dpm', 'box_odpm', 'box_ddpm', 'on_off_odpm', 'on_off_ddpm']
missing_count = merged_df_2017_2018[darko_cols].isnull().any(axis=1).sum()
print(f"Rows with missing DARKO metrics: {missing_count}")

# If there are missing values, examine which players
if missing_count > 0:
    missing_players = merged_df_2017_2018[merged_df_2017_2018[darko_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players with missing data: {missing_players}")

print(merged_df_2017_2018.columns)
#print(merged_df_2017_2018.loc[merged_df_2017_2018['player_name']=='zhou qi'])
merged_df_2017_2018 = pd.merge(merged_df_2017_2018,lebron, on=['player_name','season'], how='left')
print(merged_df_2017_2018.columns)

lebron_cols = ['LEBRON WAR','LEBRON', 'O-LEBRON', 'D-LEBRON','Offensive Archetype', 'Defensive Role']

lebron_missing_count = merged_df_2017_2018[lebron_cols].isnull().any(axis=1).sum()
print(f"Rows with missing LEBRON metrics: {lebron_missing_count} out of {len(merged_df_2017_2018)} ({lebron_missing_count/len(merged_df_2017_2018)*100:.2f}%)")

# If there are missing values, examine which players
if lebron_missing_count > 0:
    missing_lebron_players = merged_df_2017_2018[merged_df_2017_2018[lebron_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players missing LEBRON data: {missing_lebron_players}")
    
    # Count how many rows each missing player has
    missing_counts = merged_df_2017_2018[merged_df_2017_2018[lebron_cols].isnull().any(axis=1)]['player_name'].value_counts()
    print("\nMissing row counts by player:")
    print(missing_counts)
else:
    print("All rows have complete LEBRON data!")

merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'dakari johnson', 'D-LEBRON'] = 0.37
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'dakari johnson', 'Offensive Archetype'] = 'Post Scorer'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'dakari johnson', 'Defensive Role'] = 'Helper'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'dakari johnson', 'Rotation Role'] = 'Garbage Time'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'dakari johnson', 'LEBRON WAR'] = 0.15
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'dakari johnson', 'O-LEBRON'] = -1.26
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'dakari johnson', 'LEBRON'] = -0.89

merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'josh gray', 'D-LEBRON'] = 0.39
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'josh gray', 'Offensive Archetype'] = 'Low Minute'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'josh gray', 'Defensive Role'] = 'Point of Attack'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'josh gray', 'Rotation Role'] = 'Too Few Games'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'josh gray', 'LEBRON WAR'] = 0.15
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'josh gray', 'O-LEBRON'] = -0.03
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'josh gray', 'LEBRON'] = 0.37

merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'walter lemon', 'D-LEBRON'] = -0.59
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'walter lemon', 'Offensive Archetype'] = 'Low Minute'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'walter lemon', 'Defensive Role'] = 'Point of Attack'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'walter lemon', 'Rotation Role'] = 'Too Few Games'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'walter lemon', 'LEBRON WAR'] = 0.03
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'walter lemon', 'O-LEBRON'] = -0.48
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'walter lemon', 'LEBRON'] = -1.07

merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'xavier rathan-mayes', 'D-LEBRON'] = 0.06
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'xavier rathan-mayes', 'Offensive Archetype'] = 'Primary Ball Handler'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'xavier rathan-mayes', 'Defensive Role'] = 'Point of Attack'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'xavier rathan-mayes', 'Rotation Role'] = 'Too Few Games'
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'xavier rathan-mayes', 'LEBRON WAR'] = 0.13
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'xavier rathan-mayes', 'O-LEBRON'] = -0.72
merged_df_2017_2018.loc[merged_df_2017_2018['player_name'] == 'xavier rathan-mayes', 'LEBRON'] = -0.66

"""TY LAWSON MISSING DATA"""

#print(merged_df_2016_2017.loc[merged_df_2016_2017['player_name']=='elliot williams'])
merged_df_2017_2018.to_excel('../../data/processed_2018.xlsx', index=False)