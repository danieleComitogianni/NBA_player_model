import pandas as pd
import os

def merge_player_team_data(season, base_dir='../../data/'):
    """
    Merge player-level and team-level NBA datasets for a specific season.
    
    Args:
        season (int or str): The NBA season year (e.g., 2015, 2024)
        base_dir (str): Base directory for data files
        
    Returns:
        pd.DataFrame: The merged dataset
    """
    # Define file paths
    player_file = os.path.join(base_dir, f'feature_engineer/feature_engineered_{season}.xlsx')
    team_file = os.path.join(base_dir, f'team_level_stats/nba_{season}_team_metrics.csv')
    output_file = os.path.join(base_dir, f'feature_reduction/merged_{season}.xlsx')
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Load player dataset
    player_df = pd.read_excel(player_file)
    print(f"Player dataset loaded with {player_df.shape[0]} rows and {player_df.shape[1]} columns.")
    
    # Load team dataset
    team_df = pd.read_csv(team_file)
    print(f"Team dataset loaded with {team_df.shape[0]} rows and {team_df.shape[1]} columns.")
    
    # Rename columns in team dataset to match player dataset
    team_df.rename(columns={
        'GAME-ID': 'game_id',
        'DATE': 'date',
        'TEAM': 'team_name'
    }, inplace=True)
    
    # Convert date columns to datetime
    player_df['date'] = pd.to_datetime(player_df['date'])
    team_df['date'] = pd.to_datetime(team_df['date'])
    
    # Print team dataset columns
    print("Team dataset columns:", team_df.columns.tolist())
    
    # Drop unnecessary columns from team dataset
    columns_to_drop = [
        'FG', 'FGA', '3P','3PA', 'FT', 'FTA', 'OR', 'DR', 'TOT', 'A', 'PF', 'ST', 'TO', 'BL', 'PTS',
        'POSS', 'OEFF', 'DEFF', 'cum_league_avg_oeff', 'cum_league_avg_deff',
        'cum_league_avg_pace', 'ast_rate'
    ]
    
    # Only drop columns that exist
    cols_to_drop = [col for col in columns_to_drop if col in team_df.columns]
    team_df = team_df.drop(columns=cols_to_drop)
    
    # Perform validation before merge
    validate_before_merge(player_df, team_df)
    
    # Merge datasets
    merged_df = pd.merge(player_df, team_df, on=['game_id', 'date', 'team_name'], how='left')
    print(f"Merged dataset has {merged_df.shape[0]} rows and {merged_df.shape[1]} columns.")
    
    # Save merged dataset
    merged_df.to_excel(output_file, index=False)
    print(f"Merged dataset saved to {output_file}")
    
    # Print merged dataset info
    print("Merged dataset info:")
    print(merged_df.info())
    
    # Validate after merge
    validate_after_merge(player_df, team_df, merged_df)
    
    return merged_df

def validate_before_merge(player_df, team_df):
    """
    Validate datasets before merging to identify potential issues.
    
    Args:
        player_df (pd.DataFrame): Player-level dataset
        team_df (pd.DataFrame): Team-level dataset
    """
    print("\n=== Validation Before Merge ===")
    
    # Check for duplicates in keys
    player_keys = player_df[['game_id', 'date', 'team_name']].drop_duplicates()
    team_keys = team_df[['game_id', 'date', 'team_name']].drop_duplicates()
    
    print(f"Unique key combinations in player data: {len(player_keys)}")
    print(f"Unique key combinations in team data: {len(team_keys)}")
    
    # Check for unique team names
    player_teams = player_df['team_name'].unique()
    team_teams = team_df['team_name'].unique()
    
    print(f"Unique team names in player data: {len(player_teams)}")
    print(f"Unique team names in team data: {len(team_teams)}")
    
    # Check for team name mismatches
    player_teams_set = set(player_teams)
    team_teams_set = set(team_teams)
    
    player_only = player_teams_set - team_teams_set
    team_only = team_teams_set - player_teams_set
    
    if player_only:
        print(f"Teams only in player data: {player_only}")
    
    if team_only:
        print(f"Teams only in team data: {team_only}")

def validate_after_merge(player_df, team_df, merged_df):
    """
    Validate the merged dataset to confirm successful merge.
    
    Args:
        player_df (pd.DataFrame): Player-level dataset
        team_df (pd.DataFrame): Team-level dataset
        merged_df (pd.DataFrame): Merged dataset
    """
    print("\n=== Validation After Merge ===")
    
    # Identify team-specific columns
    team_columns = [col for col in merged_df.columns if col in team_df.columns 
                  and col not in ['game_id', 'date', 'team_name']]
    
    # Check for missing values in team columns
    missing_counts = merged_df[team_columns].isnull().sum()
    missing_cols = missing_counts[missing_counts > 0]
    
    if len(missing_cols) > 0:
        print("Columns with missing values:")
        print(missing_cols)
        
        # Calculate percentage of rows with any team data missing
        rows_with_missing = merged_df[team_columns].isnull().any(axis=1).sum()
        pct_missing = (rows_with_missing / len(merged_df)) * 100
        print(f"Percentage of rows with missing team data: {pct_missing:.2f}%")
    else:
        print("No missing values found in team columns - merge successful!")

# Example usage
if __name__ == "__main__":
    
    # Merge data for multiple seasons
    seasons = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    for season in seasons:
        try:
            print(f"\n{'='*50}\nProcessing season {season}\n{'='*50}")
            merge_player_team_data(season)
        except FileNotFoundError as e:
            print(f"Error processing season {season}: {e}")