import pandas as pd
import re

pd.set_option('display.max_columns', None)
darko_df = pd.read_excel('../../data/DARKO.xlsx')
box_score_2014 = pd.read_excel('../../data/boxscore_2014.xlsx')
lebron = pd.read_excel('../../data/lebron_processed.xlsx')
#OK i have the dataframe for darko, now I want to filter the dataframe so it removes every instance under 2014
filtered_darko_df = darko_df[darko_df['season']>=2015]
filtered_darko_df = filtered_darko_df[filtered_darko_df['season']<2025]
#okay now I have the years 2014 to 2024 for darko, now Its time to merge wi
box_score_2014['DATE'] = pd.to_datetime(box_score_2014['DATE'])
box_score_2014.insert(3,'season',2015)

def clean_name(name):
    name = name.lower().strip()
    name = re.sub(r'[.,]','',name)
    name = re.sub(r'\bsr\b','',name)
    name = re.sub(r'\b(sr|jr|ii|iii|iv)\b', '', name)
    return name.strip()

box_score_2014 = box_score_2014.rename(columns={'OWN \nTEAM':'team_name','PLAYER \nFULL NAME': 'player_name', 'DAYS\nREST':'rest_days', 'STARTER\n(Y/N)': 'starter(y/n)','GAME-ID':'game_id','DATE':'date','PLAYER-ID':'player_id','POSITION':'position','OPPONENT \nTEAM':'opponent_team', 'VENUE\n(R/H)':'venue(R/H)','STARTER\n(Y/N)':'starter(Y/N)','USAGE \nRATE (%)':'usage_rate(%)'})
filtered_darko_df.drop(columns=['nba_id'], inplace=True)
filtered_darko_df.drop(columns=['team_name'], inplace=True)

box_score_2014['player_name'] = box_score_2014['player_name'].apply(clean_name)
filtered_darko_df['player_name'] = filtered_darko_df['player_name'].apply(clean_name)

merged_df_2014_2015 = pd.merge(box_score_2014,filtered_darko_df, on=['player_name','season'], how='left')
print(merged_df_2014_2015.info())
print(merged_df_2014_2015.tail(5))

# Count rows with missing DARKO metrics
darko_cols = ['age', 'tm_id', 'dpm', 'o_dpm', 'd_dpm', 'box_odpm', 'box_ddpm', 'on_off_odpm', 'on_off_ddpm']
missing_count = merged_df_2014_2015[darko_cols].isnull().any(axis=1).sum()
print(f"Rows with missing DARKO metrics: {missing_count}")

# If there are missing values, examine which players
if missing_count > 0:
    missing_players = merged_df_2014_2015[merged_df_2014_2015[darko_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players with missing data: {missing_players}")



merged_df_2014_2015 = pd.merge(merged_df_2014_2015,lebron, on=['player_name','season'], how='left')

print(merged_df_2014_2015.columns)

lebron_cols = ['LEBRON WAR','LEBRON', 'O-LEBRON', 'D-LEBRON','Offensive Archetype', 'Defensive Role']

lebron_missing_count = merged_df_2014_2015[lebron_cols].isnull().any(axis=1).sum()
print(f"Rows with missing LEBRON metrics: {lebron_missing_count} out of {len(merged_df_2014_2015)} ({lebron_missing_count/len(merged_df_2014_2015)*100:.2f}%)")

# If there are missing values, examine which players
if lebron_missing_count > 0:
    missing_lebron_players = merged_df_2014_2015[merged_df_2014_2015[lebron_cols].isnull().any(axis=1)]['player_name'].unique()
    print(f"Players missing LEBRON data: {missing_lebron_players}")
    
    # Count how many rows each missing player has
    missing_counts = merged_df_2014_2015[merged_df_2014_2015[lebron_cols].isnull().any(axis=1)]['player_name'].value_counts()
    print("\nMissing row counts by player:")
    print(missing_counts)
else:
    print("All rows have complete LEBRON data!")

merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'terrence jones', 'D-LEBRON'] = 0.03
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'terrence jones', 'Offensive Archetype'] = 'Post Scorer'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'terrence jones', 'Defensive Role'] = 'Helper'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'terrence jones', 'Rotation Role'] = 'Key Rotation'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'terrence jones', 'LEBRON WAR'] = 0.96
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'terrence jones', 'O-LEBRON'] = -0.70
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'terrence jones', 'LEBRON'] = -0.67

merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jeff adrien', 'D-LEBRON'] = 0.60
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jeff adrien', 'Offensive Archetype'] = 'Post Scorer'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jeff adrien', 'Defensive Role'] = 'Helper'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jeff adrien', 'Rotation Role'] = 'Garbage Time'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jeff adrien', 'LEBRON WAR'] = 0.33
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jeff adrien', 'O-LEBRON'] = -0.58
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jeff adrien', 'LEBRON'] = 0.02

merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'elliot williams', 'D-LEBRON'] = -0.61
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'elliot williams', 'Offensive Archetype'] = 'Movement Shooter'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'elliot williams', 'Defensive Role'] = 'Wing Stopper'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'elliot williams', 'Rotation Role'] = 'Too Few Games'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'elliot williams', 'LEBRON WAR'] = 0.08
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'elliot williams', 'O-LEBRON'] = -0.61
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'elliot williams', 'LEBRON'] = -1.23

merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'will cherry', 'D-LEBRON'] = -0.41
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'will cherry', 'Offensive Archetype'] = 'Low Minute'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'will cherry', 'Defensive Role'] = 'Point of Attack'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'will cherry', 'Rotation Role'] = 'Too Few Games'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'will cherry', 'LEBRON WAR'] = 0.05
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'will cherry', 'O-LEBRON'] = -0.72
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'will cherry', 'LEBRON'] = -1.13

merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'patrick christopher', 'D-LEBRON'] = -0.32
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'patrick christopher', 'Offensive Archetype'] = 'Low Minute'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'patrick christopher', 'Defensive Role'] = 'Chaser'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'patrick christopher', 'Rotation Role'] = 'Too Few Games'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'patrick christopher', 'LEBRON WAR'] = 0.03
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'patrick christopher', 'O-LEBRON'] = -0.38
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'patrick christopher', 'LEBRON'] = -0.70

merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jerrelle benimon', 'D-LEBRON'] = -0.34
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jerrelle benimon', 'Offensive Archetype'] = 'Low Minute'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jerrelle benimon', 'Defensive Role'] = 'Helper'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jerrelle benimon', 'Rotation Role'] = 'Too Few Games'
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jerrelle benimon', 'LEBRON WAR'] = 0.00
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jerrelle benimon', 'O-LEBRON'] = -0.09
merged_df_2014_2015.loc[merged_df_2014_2015['player_name'] == 'jerrelle benimon', 'LEBRON'] = -0.44

print(merged_df_2014_2015.loc[merged_df_2014_2015['player_name']=='elliot williams'])
merged_df_2014_2015.to_excel('../../data/processed_2015.xlsx', index=False)