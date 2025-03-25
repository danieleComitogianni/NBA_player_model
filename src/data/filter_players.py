import pandas as pd

# Load the processed dataset
box_score = pd.read_excel('../../data/processed_2015.xlsx')

# Filter for LA Lakers games (using case-insensitive matching on team_name)
lakers_games = box_score[box_score['team_name'].str.lower() == 'la lakers'].copy()

# Check if any games are found
if lakers_games.empty:
    raise ValueError("No data found for LA Lakers. Verify the team_name values in your data.")

# Convert the date column to datetime and sort by date
lakers_games['date'] = pd.to_datetime(lakers_games['date'])
lakers_games = lakers_games.sort_values('date')

# Select one player: for instance, choose the first unique player in the filtered data
unique_players = lakers_games['player_name'].unique()
if len(unique_players) == 0:
    raise ValueError("No players found in the dataset.")

selected_player = unique_players[0]
print(f"Selected player: {selected_player}")

# Filter the games for that specific player and sort by date
player_games = lakers_games[lakers_games['player_name'] == selected_player].copy()
player_games = player_games.sort_values('date')

# Extract the first 10 games for the selected player
first_10_games = player_games.head(10)
first_10_games.to_excel('../../data/sample_2015.xlsx')


# Print the player name, date, and game_id for these 10 games
print(first_10_games[:2])
