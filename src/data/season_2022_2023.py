import pandas as pd
import re

pd.set_option('display.max_columns', None)
darko_df = pd.read_excel('../../data/DARKO.xlsx')
box_score_2022 = pd.read_excel('../../data/boxscore_2022.xlsx')
lebron = pd.read_excel('../../data/lebron_processed.xlsx')
#OK i have the dataframe for darko, now I want to filter the dataframe so it removes every instance under 2014
filtered_darko_df = darko_df[darko_df['season']>=2015]
filtered_darko_df = filtered_darko_df[filtered_darko_df['season']<2025]

box_score_2022['DATE'] = pd.to_datetime(box_score_2022['DATE'])
box_score_2022.insert(3,'season',2023)

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
        'didi louzada':'marcos louzada silva',
        'nic claxton': 'nicolas claxton',
        'enes freedom': 'enes kanter',
        'bones hyland':"nah'shon hyland"
    }
    
    # Apply specific mappings if name is in the dictionary
    if name in name_mapping:
        return name_mapping[name]
    
    # Final cleanup - remove extra spaces
    return re.sub(r'\s+', ' ', name).strip()

box_score_2022 = box_score_2022.rename(columns={'OWN \nTEAM':'team_name','PLAYER \nFULL NAME': 'player_name', 'DAYS\nREST':'rest_days', 'STARTER\n(Y/N)': 'starter(y/n)','GAME-ID':'game_id','DATE':'date','PLAYER-ID':'player_id','POSITION':'position','OPPONENT \nTEAM':'opponent_team', 'VENUE\n(R/H)':'venue(R/H)','STARTER\n(Y/N)':'starter(Y/N)','USAGE \nRATE (%)':'usage_rate(%)'})
filtered_darko_df.drop(columns=['nba_id'], inplace=True)
filtered_darko_df.drop(columns=['team_name'], inplace=True)

box_score_2022['player_name'] = box_score_2022['player_name'].apply(clean_name)
filtered_darko_df['player_name'] = filtered_darko_df['player_name'].apply(clean_name)

merged_df_2022_2023 = pd.merge(box_score_2022,filtered_darko_df, on=['player_name','season'], how='left')
print(merged_df_2022_2023.info())
print(merged_df_2022_2023[:5])
print(merged_df_2022_2023.tail(5))

# Count rows with missing DARKO metrics
darko_cols = ['age', 'tm_id', 'dpm', 'o_dpm', 'd_dpm', 'box_odpm', 'box_ddpm', 'on_off_odpm', 'on_off_ddpm']
missing_count = merged_df_2022_2023[darko_cols].isnull().any(axis=1).sum()
print(f"Rows with missing DARKO metrics: {missing_count}")

# If there are missing values, examine which players
if missing_count > 0:
    missing_players = merged_df_2022_2023[merged_df_2022_2023[darko_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players with missing data: {missing_players}")

print(merged_df_2022_2023.columns)
print(merged_df_2022_2023.loc[merged_df_2022_2023['player_name']=="kenyon martin"])
merged_df_2022_2023 = pd.merge(merged_df_2022_2023,lebron, on=['player_name','season'], how='left')
print(merged_df_2022_2023.columns)

lebron_cols = ['LEBRON WAR','LEBRON', 'O-LEBRON', 'D-LEBRON','Offensive Archetype', 'Defensive Role','Rotation Role']

"""Manually inserting calculated stats for players missing data from my LEBRON dataset"""

merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'moritz wagner', 'D-LEBRON'] = 0.32
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'moritz wagner', 'Offensive Archetype'] = 'Stretch Big'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'moritz wagner', 'Defensive Role'] = 'Mobile Big'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'moritz wagner', 'Rotation Role'] = 'Rotation'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'moritz wagner', 'LEBRON WAR'] = 2.37
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'moritz wagner', 'O-LEBRON'] = 0.63
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'moritz wagner', 'LEBRON'] = 0.95


merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'john konchar', 'D-LEBRON'] = 0.64
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'john konchar', 'Offensive Archetype'] = 'Movement Shooter'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'john konchar', 'Defensive Role'] = 'Point of Attack'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'john konchar', 'Rotation Role'] = 'Key Rotation'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'john konchar', 'LEBRON WAR'] = 2.11
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'john konchar', 'O-LEBRON'] = -0.85
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'john konchar', 'LEBRON'] = -0.20

"""TRISTAN THOMPSON, 6 GAMES, NO LEBRON DATA"""

merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'lester quinones', 'D-LEBRON'] = -0.18
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'lester quinones', 'Offensive Archetype'] = 'Low Minute'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'lester quinones', 'Defensive Role'] = 'Helper'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'lester quinones', 'Rotation Role'] = 'Too Few Games'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'lester quinones', 'LEBRON WAR'] = 0.02
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'lester quinones', 'O-LEBRON'] = -0.12
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'lester quinones', 'LEBRON'] = -0.30

merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'deonte burton', 'D-LEBRON'] = -0.11
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'deonte burton', 'Offensive Archetype'] = 'Low Minute'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'deonte burton', 'Defensive Role'] = 'Mobile Big'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'deonte burton', 'Rotation Role'] = 'Too Few Games'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'deonte burton', 'LEBRON WAR'] = 0.01
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'deonte burton', 'O-LEBRON'] = -0.19
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'deonte burton', 'LEBRON'] = -0.30

"""DAQUAN JEFFERIES, 6 GAMES, NO LEBRON DATA"""

merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'frank jackson', 'D-LEBRON'] = -0.21
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'frank jackson', 'Offensive Archetype'] = 'Low Minute'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'frank jackson', 'Defensive Role'] = 'Anchor Big'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'frank jackson', 'Rotation Role'] = 'Too Few Games'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'frank jackson', 'LEBRON WAR'] = 0.01
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'frank jackson', 'O-LEBRON'] = -0.03
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'frank jackson', 'LEBRON'] = -0.24

merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'daquan jeffries', 'D-LEBRON'] = -0.41
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'daquan jeffries', 'Offensive Archetype'] = 'Low Minute'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'daquan jeffries', 'Defensive Role'] = 'Low Activity'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'daquan jeffries', 'Rotation Role'] = 'Garbage Time'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'daquan jeffries', 'LEBRON WAR'] = 0.03
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'daquan jeffries', 'O-LEBRON'] = -0.62
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'daquan jeffries', 'LEBRON'] = -1.03

merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'tristan thompson', 'D-LEBRON'] = 0.05
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'tristan thompson', 'Offensive Archetype'] = 'Roll + Cut Big'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'tristan thompson', 'Defensive Role'] = 'Mobile Big'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'tristan thompson', 'Rotation Role'] = 'Rotation'
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'tristan thompson', 'LEBRON WAR'] = 1.00
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'tristan thompson', 'O-LEBRON'] = -0.4
merged_df_2022_2023.loc[merged_df_2022_2023['player_name'] == 'tristan thompson', 'LEBRON'] = -0.35


lebron_missing_count = merged_df_2022_2023[lebron_cols].isnull().any(axis=1).sum()
print(f"Rows with missing LEBRON metrics: {lebron_missing_count} out of {len(merged_df_2022_2023)} ({lebron_missing_count/len(merged_df_2022_2023)*100:.2f}%)")

# If there are missing values, examine which players
if lebron_missing_count > 0:
    missing_lebron_players = merged_df_2022_2023[merged_df_2022_2023[lebron_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players missing LEBRON data: {missing_lebron_players}")
    
    # Count how many rows each missing player has
    missing_counts = merged_df_2022_2023[merged_df_2022_2023[lebron_cols].isnull().any(axis=1)]['player_name'].value_counts()
    print("\nMissing row counts by player:")
    print(missing_counts)
else:
    print("All rows have complete LEBRON data!")


#print(merged_df_2022_2023.loc[merged_df_2022_2023['player_name']=='daquan jeffries'])
merged_df_2022_2023.to_excel('../../data/processed_2023.xlsx', index=False)