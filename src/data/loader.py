import pandas as pd
import re

pd.set_option('display.max_columns', None)
darko_df = pd.read_excel('../../data/DARKO.xlsx')
box_score_2014 = pd.read_excel('../../data/boxscore_2014.xlsx')
#OK i have the dataframe for darko, now I want to filter the dataframe so it removes every instance under 2014
filtered_darko_df = darko_df[darko_df['season']>=2014]
filtered_darko_df = filtered_darko_df[filtered_darko_df['season']<2025]
#okay now I have the years 2014 to 2024 for darko, now Its time to merge wi
box_score_2014['DATE'] = pd.to_datetime(box_score_2014['DATE'])
years = [date.year for date in box_score_2014['DATE']]
box_score_2014.insert(3,'season',years)

def clean_name(name):
    name = name.lower().strip()
    name = re.sub(r'[.,]','',name)
    name = re.sub(r'\bsr\b','',name)
    return name.strip()

box_score_2014 = box_score_2014.rename(columns={'PLAYER \nFULL NAME': 'player_name'})
filtered_darko_df.drop(columns=['nba_id'], inplace=True)
print(box_score_2014.info())
box_score_2014['player_name'] = box_score_2014['player_name'].apply(clean_name)
filtered_darko_df['player_name'] = filtered_darko_df['player_name'].apply(clean_name)
box_players = set(box_score_2014['player_name'])
darko_players = set(filtered_darko_df['player_name'])
print(box_players.difference(darko_players))
merged_df = pd.merge(box_score_2014,filtered_darko_df, on=['player_name','season'], how='left')
print(merged_df.info())

darko_cols = ['age', 'tm_id', 'team_name', 'dpm', 'o_dpm', 'd_dpm', 'box_odpm', 'box_ddpm', 'on_off_odpm', 'on_off_ddpm']
missing_darko = merged_df[merged_df[darko_cols].isnull().any(axis=1)]
unmatched = merged_df[merged_df['age'].isnull()]
print(unmatched)
missing_players = unmatched['player_name'].unique()
print(missing_players)
missing_seasons = unmatched['season'].unique()
print(missing_seasons)


