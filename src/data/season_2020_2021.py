import pandas as pd
import re

pd.set_option('display.max_columns', None)
darko_df = pd.read_excel('../../data/DARKO.xlsx')
box_score_2020 = pd.read_excel('../../data/boxscore_2020.xlsx')
lebron = pd.read_excel('../../data/lebron_processed.xlsx')
#OK i have the dataframe for darko, now I want to filter the dataframe so it removes every instance under 2014
filtered_darko_df = darko_df[darko_df['season']>=2015]
filtered_darko_df = filtered_darko_df[filtered_darko_df['season']<2025]

box_score_2020['DATE'] = pd.to_datetime(box_score_2020['DATE'])
box_score_2020.insert(3,'season',2021)

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
    
    if 'charlie' in name and 'brown' in name:
        print(f"Found name containing 'charlie' and 'brown': {repr(name)}")
        return 'charles brown'
    
    # Handle specific name variations
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
        'didi louzada':'marcos louzada silva'
    }
    
    # Apply specific mappings if name is in the dictionary
    if name in name_mapping:
        return name_mapping[name]
    
    # Final cleanup - remove extra spaces
    return re.sub(r'\s+', ' ', name).strip()

box_score_2020 = box_score_2020.rename(columns={'OWN \nTEAM':'team_name','PLAYER \nFULL NAME': 'player_name', 'DAYS\nREST':'rest_days', 'STARTER\n(Y/N)': 'starter(y/n)','GAME-ID':'game_id','DATE':'date','PLAYER-ID':'player_id','POSITION':'position','OPPONENT \nTEAM':'opponent_team', 'VENUE\n(R/H)':'venue(R/H)','STARTER\n(Y/N)':'starter(Y/N)','USAGE \nRATE (%)':'usage_rate(%)'})
filtered_darko_df.drop(columns=['nba_id'], inplace=True)
filtered_darko_df.drop(columns=['team_name'], inplace=True)

box_score_2020['player_name'] = box_score_2020['player_name'].apply(clean_name)
filtered_darko_df['player_name'] = filtered_darko_df['player_name'].apply(clean_name)

merged_df_2020_2021 = pd.merge(box_score_2020,filtered_darko_df, on=['player_name','season'], how='left')
print(merged_df_2020_2021.info())
print(merged_df_2020_2021[:5])
print(merged_df_2020_2021.tail(5))

# Count rows with missing DARKO metrics
darko_cols = ['age', 'tm_id', 'dpm', 'o_dpm', 'd_dpm', 'box_odpm', 'box_ddpm', 'on_off_odpm', 'on_off_ddpm']
missing_count = merged_df_2020_2021[darko_cols].isnull().any(axis=1).sum()
print(f"Rows with missing DARKO metrics: {missing_count}")

# If there are missing values, examine which players
if missing_count > 0:
    missing_players = merged_df_2020_2021[merged_df_2020_2021[darko_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players with missing data: {missing_players}")

print(merged_df_2020_2021.columns)
#print(merged_df_2020_2021.loc[merged_df_2020_2021['player_name']=='charles brown'])
merged_df_2020_2021 = pd.merge(merged_df_2020_2021,lebron, on=['player_name','season'], how='left')
print(merged_df_2020_2021.columns)

lebron_cols = ['LEBRON WAR','LEBRON', 'O-LEBRON', 'D-LEBRON','Offensive Archetype', 'Defensive Role']

lebron_missing_count = merged_df_2020_2021[lebron_cols].isnull().any(axis=1).sum()
print(f"Rows with missing LEBRON metrics: {lebron_missing_count} out of {len(merged_df_2020_2021)} ({lebron_missing_count/len(merged_df_2020_2021)*100:.2f}%)")

# If there are missing values, examine which players
if lebron_missing_count > 0:
    missing_lebron_players = merged_df_2020_2021[merged_df_2020_2021[lebron_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players missing LEBRON data: {missing_lebron_players}")
    
    # Count how many rows each missing player has
    missing_counts = merged_df_2020_2021[merged_df_2020_2021[lebron_cols].isnull().any(axis=1)]['player_name'].value_counts()
    print("\nMissing row counts by player:")
    print(missing_counts)
else:
    print("All rows have complete LEBRON data!")


merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'moritz wagner', 'D-LEBRON'] = 0.47
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'moritz wagner', 'Offensive Archetype'] = 'Stretch Big'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'moritz wagner', 'Defensive Role'] = 'Helper'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'moritz wagner', 'Rotation Role'] = 'Rotation'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'moritz wagner', 'LEBRON WAR'] = 0.84
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'moritz wagner', 'O-LEBRON'] = -1.06
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'moritz wagner', 'LEBRON'] = -0.59


merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'john konchar', 'D-LEBRON'] = -0.30
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'john konchar', 'Offensive Archetype'] = 'Stationary Shooter'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'john konchar', 'Defensive Role'] = 'Chaser'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'john konchar', 'Rotation Role'] = 'Rotation'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'john konchar', 'LEBRON WAR'] = 0.51
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'john konchar', 'O-LEBRON'] = -0.72
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'john konchar', 'LEBRON'] = -1.02

merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'frank jackson', 'D-LEBRON'] = -1.99
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'frank jackson', 'Offensive Archetype'] = 'Off Screen Shooter'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'frank jackson', 'Defensive Role'] = 'Chaser'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'frank jackson', 'Rotation Role'] = 'Rotation'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'frank jackson', 'LEBRON WAR'] = -0.07
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'frank jackson', 'O-LEBRON'] = -0.57
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'frank jackson', 'LEBRON'] = -2.55

merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin james', 'D-LEBRON'] = -0.74
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin james', 'Offensive Archetype'] = 'Low Minute'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin james', 'Defensive Role'] = 'Chaser'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin james', 'Rotation Role'] = 'Garbage Time'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin james', 'LEBRON WAR'] = 0.03
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin james', 'O-LEBRON'] = -1.50
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin james', 'LEBRON'] = -2.25

merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin robinson', 'D-LEBRON'] = -0.06
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin robinson', 'Offensive Archetype'] = 'Low Minute'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin robinson', 'Defensive Role'] = 'Point of Attack'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin robinson', 'Rotation Role'] = 'Garbage Time'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin robinson', 'LEBRON WAR'] = 0.10
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin robinson', 'O-LEBRON'] = -0.63
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'justin robinson', 'LEBRON'] = -0.69

merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'donta hall', 'D-LEBRON'] = 0.77
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'donta hall', 'Offensive Archetype'] = 'Athletic Finisher'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'donta hall', 'Defensive Role'] = 'Anchor Big'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'donta hall', 'Rotation Role'] = 'Garbage Time'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'donta hall', 'LEBRON WAR'] = 0.24
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'donta hall', 'O-LEBRON'] = -1.11
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'donta hall', 'LEBRON'] = -0.34

merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'norvel pelle', 'D-LEBRON'] = -0.15
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'norvel pelle', 'Offensive Archetype'] = 'Low Minute'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'norvel pelle', 'Defensive Role'] = 'Anchor Big'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'norvel pelle', 'Rotation Role'] = 'Garbage Time'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'norvel pelle', 'LEBRON WAR'] = 0.08
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'norvel pelle', 'O-LEBRON'] = -0.72
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'norvel pelle', 'LEBRON'] = -0.87

merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'jeremiah martin', 'D-LEBRON'] = -0.26
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'jeremiah martin', 'Offensive Archetype'] = 'Low Minute'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'jeremiah martin', 'Defensive Role'] = 'Point of Attack'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'jeremiah martin', 'Rotation Role'] = 'Garbage Time'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'jeremiah martin', 'LEBRON WAR'] = 0.09
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'jeremiah martin', 'O-LEBRON'] = -0.32
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'jeremiah martin', 'LEBRON'] = -0.58

merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'Cam Reynolds', 'D-LEBRON'] = -0.20
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'Cam Reynolds', 'Offensive Archetype'] = 'Low Minute'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'Cam Reynolds', 'Defensive Role'] = 'Helper'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'Cam Reynolds', 'Rotation Role'] = 'Too Few Games'
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'Cam Reynolds', 'LEBRON WAR'] = 0.05
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'Cam Reynolds', 'O-LEBRON'] = -0.35
merged_df_2020_2021.loc[merged_df_2020_2021['player_name'] == 'Cam Reynolds', 'LEBRON'] = -0.54

#print(merged_df_2016_2017.loc[merged_df_2016_2017['player_name']=='elliot williams'])
merged_df_2020_2021.to_excel('../../data/processed_2021.xlsx', index=False)
