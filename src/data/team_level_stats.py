import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)

# Load data
team_df = pd.read_excel('../../data/2014-2015_NBA_Box_Score_Team-Stats.xlsx')
print(team_df.columns)

# Select relevant columns
keep_columns = [
  'GAME-ID', 'DATE', 'TEAM', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA',
  'OR', 'DR', 'TOT', 'A', 'PF', 'ST', 'TO', 'BL', 'PTS', 'POSS', 'PACE', 'OEFF', 'DEFF'
]
df = team_df[keep_columns].copy()
print(df.columns)

# Convert dates and sort chronologically
df['DATE'] = pd.to_datetime(df['DATE'])
df = df.sort_values('DATE')

# Calculate daily and cumulative league averages
daily_avg = df.groupby('DATE').agg({
  'OEFF': 'mean',
  'DEFF': 'mean'
}).rename(columns={
  'OEFF': 'daily_avg_oeff',
  'DEFF': 'daily_avg_deff'
}).reset_index()

daily_avg['cum_league_avg_oeff'] = daily_avg['daily_avg_oeff'].expanding().mean().shift(1)
daily_avg['cum_league_avg_deff'] = daily_avg['daily_avg_deff'].expanding().mean().shift(1)
daily_avg['cum_league_avg_oeff'] = daily_avg['cum_league_avg_oeff'].fillna(daily_avg['daily_avg_oeff'])
daily_avg['cum_league_avg_deff'] = daily_avg['cum_league_avg_deff'].fillna(daily_avg['daily_avg_deff'])

df = pd.merge(df, daily_avg[['DATE', 'cum_league_avg_oeff', 'cum_league_avg_deff']], on='DATE', how='left')

# Create a dictionary to track team stats cumulatively
team_stats = {}

# Initialize dictionary to store team stats with league average defaults
for team in df['TEAM'].unique():
  team_stats[team] = {
      'oeff_sum': 0,
      'deff_sum': 0,
      'games': 0
  }

# Add columns for adjusted metrics
df['team_avg_oeff'] = np.nan
df['team_avg_deff'] = np.nan
df['opp_avg_oeff'] = np.nan
df['opp_avg_deff'] = np.nan
df['adj_oeff'] = np.nan
df['adj_deff'] = np.nan

# Get first day league averages to use for teams with no history
first_day = df['DATE'].min()
first_day_oeff = df[df['DATE'] == first_day]['OEFF'].mean()
first_day_deff = df[df['DATE'] == first_day]['DEFF'].mean()

# FIRST PASS: Calculate team averages for all games
for idx, row in df.iterrows():
  team = row['TEAM']
  
  # Calculate and store team averages before adding the current game
  if team_stats[team]['games'] > 0:
      df.at[idx, 'team_avg_oeff'] = team_stats[team]['oeff_sum'] / team_stats[team]['games']
      df.at[idx, 'team_avg_deff'] = team_stats[team]['deff_sum'] / team_stats[team]['games']
  else:
      # For first game, use first day league average
      df.at[idx, 'team_avg_oeff'] = first_day_oeff
      df.at[idx, 'team_avg_deff'] = first_day_deff
  
  # Update team's cumulative stats for future games
  team_stats[team]['oeff_sum'] += row['OEFF']
  team_stats[team]['deff_sum'] += row['DEFF']
  team_stats[team]['games'] += 1

# SECOND PASS: Calculate opponent averages and adjusted metrics
for idx, row in df.iterrows():
  game_id = row['GAME-ID']
  team = row['TEAM']
  
  # Find opponent in this game
  opponent_row = df[(df['GAME-ID'] == game_id) & (df['TEAM'] != team)]
  if len(opponent_row) == 0:
      continue
      
  opponent = opponent_row.iloc[0]['TEAM']
  
  # Get opponent's team_avg values from their row for this game
  opp_idx = opponent_row.index[0]
  opp_avg_oeff = df.at[opp_idx, 'team_avg_oeff']
  opp_avg_deff = df.at[opp_idx, 'team_avg_deff']
  
  # Store opponent averages
  df.at[idx, 'opp_avg_oeff'] = opp_avg_oeff
  df.at[idx, 'opp_avg_deff'] = opp_avg_deff
  
  # Calculate adjusted metrics
  league_avg_oeff = row['cum_league_avg_oeff']
  league_avg_deff = row['cum_league_avg_deff']
  
  df.at[idx, 'adj_deff'] = row['DEFF'] * (opp_avg_oeff / league_avg_oeff)
  df.at[idx, 'adj_oeff'] = row['OEFF'] * (opp_avg_deff / league_avg_deff)

# Print the first 30 games for validation
validation_columns = ['GAME-ID', 'DATE', 'TEAM', 'OEFF', 'DEFF', 'team_avg_oeff', 'team_avg_deff', 'opp_avg_oeff', 'opp_avg_deff', 'adj_oeff', 'adj_deff']
print("\nFirst 30 games for validation:")
print(df[validation_columns].head(30))

# Validate both Charlotte and Golden State
teams_to_validate = ["Charlotte", "Golden State"]
validation_data = {}

for team_to_validate in teams_to_validate:
   # Get the first 10 games for this team
   team_games = df[df['TEAM'] == team_to_validate].head(10).copy()
   
   # Create a table showing how stats evolve game by game
   validate_columns = ['DATE', 'GAME-ID', 'TEAM', 'OEFF', 'DEFF', 'team_avg_oeff', 'team_avg_deff', 'cum_league_avg_oeff', 'cum_league_avg_deff', 
                      'opp_avg_oeff', 'opp_avg_deff', 'adj_oeff', 'adj_deff']
   validation_table = team_games[validate_columns].sort_values('DATE')
   
   # Store in dictionary
   validation_data[team_to_validate] = validation_table
   
   # Save to Excel
   file_name = f'../../data/{team_to_validate.lower().replace(" ", "_")}_team_validate.xlsx'
   validation_table.to_excel(file_name)

