import pandas as pd
import re

pd.set_option('display.max_columns', None)
darko_df = pd.read_excel('../../data/DARKO.xlsx')
box_score_2023 = pd.read_excel('../../data/boxscore_2023.xlsx')
lebron = pd.read_excel('../../data/lebron_processed.xlsx')
#OK i have the dataframe for darko, now I want to filter the dataframe so it removes every instance under 2014
filtered_darko_df = darko_df[darko_df['season']>=2015]
filtered_darko_df = filtered_darko_df[filtered_darko_df['season']<2025]

box_score_2023['DATE'] = pd.to_datetime(box_score_2023['DATE'])
box_score_2023.insert(3,'season',2024)

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
        'bones hyland':"nah'shon hyland",
        'nate williams':'jeenathan williams',
        'kj martin':'kenyon martin'
    }
    
    if name in name_mapping:
        return name_mapping[name]
    
    return re.sub(r'\s+', ' ', name).strip()

box_score_2023 = box_score_2023.rename(columns={'OWN \nTEAM':'team_name','PLAYER \nFULL NAME': 'player_name', 'DAYS\nREST':'rest_days', 'STARTER\n(Y/N)': 'starter(y/n)','GAME-ID':'game_id','DATE':'date','PLAYER-ID':'player_id','POSITION':'position','OPPONENT \nTEAM':'opponent_team', 'VENUE\n(R/H)':'venue(R/H)','STARTER\n(Y/N)':'starter(Y/N)','USAGE \nRATE (%)':'usage_rate(%)'})
filtered_darko_df.drop(columns=['nba_id'], inplace=True)
filtered_darko_df.drop(columns=['team_name'], inplace=True)

box_score_2023['player_name'] = box_score_2023['player_name'].apply(clean_name)
filtered_darko_df['player_name'] = filtered_darko_df['player_name'].apply(clean_name)

merged_df_2023_2024 = pd.merge(box_score_2023,filtered_darko_df, on=['player_name','season'], how='left')
print(merged_df_2023_2024.info())
print(merged_df_2023_2024[:5])
print(merged_df_2023_2024.tail(5))

# Count rows with missing DARKO metrics
darko_cols = ['age', 'tm_id', 'dpm', 'o_dpm', 'd_dpm', 'box_odpm', 'box_ddpm', 'on_off_odpm', 'on_off_ddpm']
missing_count = merged_df_2023_2024[darko_cols].isnull().any(axis=1).sum()
print(f"Rows with missing DARKO metrics: {missing_count}")

# If there are missing values, examine which players
if missing_count > 0:
    missing_players = merged_df_2023_2024[merged_df_2023_2024[darko_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players with missing data: {missing_players}")

print(merged_df_2023_2024.columns)
print(merged_df_2023_2024.loc[merged_df_2023_2024['player_name']=="royce o'neale"])
merged_df_2023_2024 = pd.merge(merged_df_2023_2024,lebron, on=['player_name','season'], how='left')
print(merged_df_2023_2024.columns)

lebron_cols = ['LEBRON WAR','LEBRON', 'O-LEBRON', 'D-LEBRON','Offensive Archetype', 'Defensive Role']

lebron_missing_count = merged_df_2023_2024[lebron_cols].isnull().any(axis=1).sum()
print(f"Rows with missing LEBRON metrics: {lebron_missing_count} out of {len(merged_df_2023_2024)} ({lebron_missing_count/len(merged_df_2023_2024)*100:.2f}%)")

# If there are missing values, examine which players
if lebron_missing_count > 0:
    missing_lebron_players = merged_df_2023_2024[merged_df_2023_2024[lebron_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players missing LEBRON data: {missing_lebron_players}")
    
    # Count how many rows each missing player has
    missing_counts = merged_df_2023_2024[merged_df_2023_2024[lebron_cols].isnull().any(axis=1)]['player_name'].value_counts()
    print("\nMissing row counts by player:")
    print(missing_counts)
else:
    print("All rows have complete LEBRON data!")

"""Manually inserting calculated stats for players missing data from my LEBRON dataset"""

merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'moritz wagner', 'D-LEBRON'] = -0.35
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'moritz wagner', 'Offensive Archetype'] = 'Roll + Cut Big'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'moritz wagner', 'Defensive Role'] = 'Mobile Big'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'moritz wagner', 'Rotation Role'] = 'Rotation'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'moritz wagner', 'LEBRON WAR'] = 2.49
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'moritz wagner', 'O-LEBRON'] = 0.7
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'moritz wagner', 'LEBRON'] = 0.35

merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'john konchar', 'D-LEBRON'] = 1.85
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'john konchar', 'Offensive Archetype'] = 'Movement Shooter'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'john konchar', 'Defensive Role'] = 'Chaser'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'john konchar', 'Rotation Role'] = 'Key Rotation'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'john konchar', 'LEBRON WAR'] = 1.33
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'john konchar', 'O-LEBRON'] = -2.5
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'john konchar', 'LEBRON'] = -0.65

merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'lester quinones', 'D-LEBRON'] = -0.65
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'lester quinones', 'Offensive Archetype'] = 'Movement Shooter'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'lester quinones', 'Defensive Role'] = 'Chaser'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'lester quinones', 'Rotation Role'] = 'Garbage Time'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'lester quinones', 'LEBRON WAR'] = 0.37
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'lester quinones', 'O-LEBRON'] = -0.29
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'lester quinones', 'LEBRON'] = -0.94

merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'taze moore', 'D-LEBRON'] = 0.08 
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'taze moore', 'Offensive Archetype'] = 'Low Minute'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'taze moore', 'Defensive Role'] = 'Helper'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'taze moore', 'Rotation Role'] = 'Too Few Games'
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'taze moore', 'LEBRON WAR'] = 0.06
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'taze moore', 'O-LEBRON'] = -0.27
merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == 'taze moore', 'LEBRON'] = -0.20

players = ['moritz wagner', 'john konchar', 'lester quinones', 'taze moore']
avg_minutes = {player: merged_df_2023_2024.loc[merged_df_2023_2024['player_name'] == player, 'MIN'].mean() for player in players}
print(avg_minutes)


#print(merged_df_2016_2017.loc[merged_df_2016_2017['player_name']=='elliot williams'])
merged_df_2023_2024.to_excel('../../data/processed_2024.xlsx', index=False)
