import pandas as pd
import re

pd.set_option('display.max_columns', None)
darko_df = pd.read_excel('../../data/DARKO.xlsx')
box_score_2019 = pd.read_excel('../../data/boxscore_2019.xlsx')
lebron = pd.read_excel('../../data/lebron_processed.xlsx')
#OK i have the dataframe for darko, now I want to filter the dataframe so it removes every instance under 2014
filtered_darko_df = darko_df[darko_df['season']>=2015]
filtered_darko_df = filtered_darko_df[filtered_darko_df['season']<2025]

box_score_2019['DATE'] = pd.to_datetime(box_score_2019['DATE'])
box_score_2019.insert(3,'season',2020)

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

box_score_2019 = box_score_2019.rename(columns={'OWN \nTEAM':'team_name','PLAYER \nFULL NAME': 'player_name', 'DAYS\nREST':'rest_days', 'STARTER\n(Y/N)': 'starter(y/n)','GAME-ID':'game_id','DATE':'date','PLAYER-ID':'player_id','POSITION':'position','OPPONENT \nTEAM':'opponent_team', 'VENUE\n(R/H)':'venue(R/H)','STARTER\n(Y/N)':'starter(Y/N)','USAGE \nRATE (%)':'usage_rate(%)'})
filtered_darko_df.drop(columns=['nba_id'], inplace=True)
filtered_darko_df.drop(columns=['team_name'], inplace=True)

box_score_2019['player_name'] = box_score_2019['player_name'].apply(clean_name)
filtered_darko_df['player_name'] = filtered_darko_df['player_name'].apply(clean_name)

merged_df_2019_2020 = pd.merge(box_score_2019,filtered_darko_df, on=['player_name','season'], how='left')
print(merged_df_2019_2020.info())
print(merged_df_2019_2020[:5])
print(merged_df_2019_2020.tail(5))

# Count rows with missing DARKO metrics
darko_cols = ['age', 'tm_id', 'dpm', 'o_dpm', 'd_dpm', 'box_odpm', 'box_ddpm', 'on_off_odpm', 'on_off_ddpm']
missing_count = merged_df_2019_2020[darko_cols].isnull().any(axis=1).sum()
print(f"Rows with missing DARKO metrics: {missing_count}")

# If there are missing values, examine which players
if missing_count > 0:
    missing_players = merged_df_2019_2020[merged_df_2019_2020[darko_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players with missing data: {missing_players}")

print(merged_df_2019_2020.columns)
#print(merged_df_2017_2018.loc[merged_df_2017_2018['player_name']=='zhou qi'])
merged_df_2019_2020 = pd.merge(merged_df_2019_2020,lebron, on=['player_name','season'], how='left')
print(merged_df_2019_2020.columns)

lebron_cols = ['LEBRON WAR','LEBRON', 'O-LEBRON', 'D-LEBRON','Offensive Archetype', 'Defensive Role']

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'moritz wagner', 'D-LEBRON'] = 1.39
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'moritz wagner', 'Offensive Archetype'] = 'Stretch Big'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'moritz wagner', 'Defensive Role'] = 'Anchor Big'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'moritz wagner', 'Rotation Role'] = 'Rotation'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'moritz wagner', 'LEBRON WAR'] = 1.05
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'moritz wagner', 'O-LEBRON'] = -1.82
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'moritz wagner', 'LEBRON'] = -0.43

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'deonte burton', 'D-LEBRON'] = -0.59
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'deonte burton', 'Offensive Archetype'] = 'Movement Shooter'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'deonte burton', 'Defensive Role'] = 'Low Activity'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'deonte burton', 'Rotation Role'] = 'Garbage Time'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'deonte burton', 'LEBRON WAR'] = -0.23
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'deonte burton', 'O-LEBRON'] = -2.78
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'deonte burton', 'LEBRON'] = -3.38


merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'john konchar', 'D-LEBRON'] = -0.10
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'john konchar', 'Offensive Archetype'] = 'Athletic Finisher'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'john konchar', 'Defensive Role'] = 'Chaser'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'john konchar', 'Rotation Role'] = 'Garbage Time'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'john konchar', 'LEBRON WAR'] = 0.19
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'john konchar', 'O-LEBRON'] = -0.61
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'john konchar', 'LEBRON'] = -0.71

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'frank jackson', 'D-LEBRON'] = -2.45
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'frank jackson', 'Offensive Archetype'] = 'Secondary Ball Handler'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'frank jackson', 'Defensive Role'] = 'Point of Attack'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'frank jackson', 'Rotation Role'] = 'Rotation'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'frank jackson', 'LEBRON WAR'] = -0.42
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'frank jackson', 'O-LEBRON'] = -0.75
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'frank jackson', 'LEBRON'] = -3.20

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin james', 'D-LEBRON'] = 0.62
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin james', 'Offensive Archetype'] = 'Low Minute'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin james', 'Defensive Role'] = 'Chaser'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin james', 'Rotation Role'] = 'Garbage Time'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin james', 'LEBRON WAR'] = 0.30
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin james', 'O-LEBRON'] = -0.98
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin james', 'LEBRON'] = -0.36

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin robinson', 'D-LEBRON'] = 0.27
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin robinson', 'Offensive Archetype'] = 'Low Minute'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin robinson', 'Defensive Role'] = 'Point of Attack'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin robinson', 'Rotation Role'] = 'Garbage Time'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin robinson', 'LEBRON WAR'] = 0.07
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin robinson', 'O-LEBRON'] = -0.40
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'justin robinson', 'LEBRON'] = -0.13

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'donta hall', 'D-LEBRON'] = 0.13
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'donta hall', 'Offensive Archetype'] = 'Athletic Finisher'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'donta hall', 'Defensive Role'] = 'Anchor Big'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'donta hall', 'Rotation Role'] = 'Too Few Games'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'donta hall', 'LEBRON WAR'] = 0.17
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'donta hall', 'O-LEBRON'] = -0.56
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'donta hall', 'LEBRON'] = -0.43

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'norvel pelle', 'D-LEBRON'] = 1.28
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'norvel pelle', 'Offensive Archetype'] = 'Roll + Cut Big'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'norvel pelle', 'Defensive Role'] = 'Anchor Big'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'norvel pelle', 'Rotation Role'] = 'Garbage Time'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'norvel pelle', 'LEBRON WAR'] = 0.16
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'norvel pelle', 'O-LEBRON'] = -2.59
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'norvel pelle', 'LEBRON'] = -1.30

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jeremiah martin', 'D-LEBRON'] = -0.19
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jeremiah martin', 'Offensive Archetype'] = 'Low Minute'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jeremiah martin', 'Defensive Role'] = 'Point of Attack'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jeremiah martin', 'Rotation Role'] = 'Garbage Time'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jeremiah martin', 'LEBRON WAR'] = 0.14
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jeremiah martin', 'O-LEBRON'] = 0.05
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jeremiah martin', 'LEBRON'] = -0.14

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh reaves', 'D-LEBRON'] = -0.38
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh reaves', 'Offensive Archetype'] = 'Low Minute'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh reaves', 'Defensive Role'] = 'Chaser'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh reaves', 'Rotation Role'] = 'Too Few Games'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh reaves', 'LEBRON WAR'] = 0.03
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh reaves', 'O-LEBRON'] = -0.32
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh reaves', 'LEBRON'] = -0.71

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'tariq owens', 'D-LEBRON'] = -0.16
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'tariq owens', 'Offensive Archetype'] = 'Low Minute'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'tariq owens', 'Defensive Role'] = 'Helper'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'tariq owens', 'Rotation Role'] = 'Too Few Games'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'tariq owens', 'LEBRON WAR'] = 0.02
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'tariq owens', 'O-LEBRON'] = -0.27
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'tariq owens', 'LEBRON'] = -0.43

"""NOTHING FOR JAYLEN ADAMS"""

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh gray', 'D-LEBRON'] = -0.03
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh gray', 'Offensive Archetype'] = 'Low Minute'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh gray', 'Defensive Role'] = 'Chaser'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh gray', 'Rotation Role'] = 'Too Few Games'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh gray', 'LEBRON WAR'] = 0.02
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh gray', 'O-LEBRON'] = -0.67
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'josh gray', 'LEBRON'] = -0.70

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'william howard', 'D-LEBRON'] = -0.58
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'william howard', 'Offensive Archetype'] = 'Low Minute'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'william howard', 'Defensive Role'] = 'Chaser'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'william howard', 'Rotation Role'] = 'Too Few Games'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'william howard', 'LEBRON WAR'] = 0.01
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'william howard', 'O-LEBRON'] = -0.09
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'william howard', 'LEBRON'] = -0.67

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jp macura', 'D-LEBRON'] = 0.47
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jp macura', 'Offensive Archetype'] = 'Low Minute'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jp macura', 'Defensive Role'] = 'Helper'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jp macura', 'Rotation Role'] = 'Too Few Games'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jp macura', 'LEBRON WAR'] = 0.00
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jp macura', 'O-LEBRON'] = 0.11
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jp macura', 'LEBRON'] = 0.58

merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jaylen adams', 'D-LEBRON'] = -0.39
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jaylen adams', 'Offensive Archetype'] = 'Low Minute'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jaylen adams', 'Defensive Role'] = 'Point of Attack'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jaylen adams', 'Rotation Role'] = 'Too Few Games'
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jaylen adams', 'LEBRON WAR'] = 0.05
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jaylen adams', 'O-LEBRON'] = -1.61
merged_df_2019_2020.loc[merged_df_2019_2020['player_name'] == 'jaylen adams', 'LEBRON'] = -2.00

lebron_missing_count = merged_df_2019_2020[lebron_cols].isnull().any(axis=1).sum()
print(f"Rows with missing LEBRON metrics: {lebron_missing_count} out of {len(merged_df_2019_2020)} ({lebron_missing_count/len(merged_df_2019_2020)*100:.2f}%)")

# If there are missing values, examine which players
if lebron_missing_count > 0:
    missing_lebron_players = merged_df_2019_2020[merged_df_2019_2020[lebron_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players missing LEBRON data: {missing_lebron_players}")
    
    # Count how many rows each missing player has
    missing_counts = merged_df_2019_2020[merged_df_2019_2020[lebron_cols].isnull().any(axis=1)]['player_name'].value_counts()
    print("\nMissing row counts by player:")
    print(missing_counts)
else:
    print("All rows have complete LEBRON data!")


#print(merged_df_2016_2017.loc[merged_df_2016_2017['player_name']=='elliot williams'])
merged_df_2019_2020.to_excel('../../data/processed_2020.xlsx', index=False)