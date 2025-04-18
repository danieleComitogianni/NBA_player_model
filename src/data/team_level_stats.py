import pandas as pd
import numpy as np
import os
import glob

pd.set_option('display.max_columns', None)

def process_season(file_path, output_dir):
    """
    Process a single NBA season file and save the results
    """
    print(f"\nProcessing: {os.path.basename(file_path)}")
    season = os.path.basename(file_path).split('_')[0]
    
    if '-' in season:
        season_year = season.split('-')[1]
    else:
        season_year = season
    
    print(f"Season: {season}, Using year {season_year} for output file")
    
    # Load data
    team_df = pd.read_excel(file_path)
    print("Original columns:", team_df.columns)
    
    # Select relevant columns
    keep_columns = [
        'GAME-ID', 'DATE', 'TEAM', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA',
        'OR', 'DR', 'TOT', 'A', 'PF', 'ST', 'TO', 'BL', 'PTS', 'POSS', 'PACE', 'OEFF', 'DEFF','OPENING SPREAD','OPENING TOTAL'
    ]
    
    # Ensure all columns exist, skip any that don't
    existing_columns = [col for col in keep_columns if col in team_df.columns]
    if len(existing_columns) < len(keep_columns):
        missing = set(keep_columns) - set(existing_columns)
        print(f"Warning: Missing columns for {season}: {missing}")
    
    df = team_df[existing_columns].copy()
    print("Selected columns:", df.columns)
    
    df['OPENING SPREAD'] = pd.to_numeric(df['OPENING SPREAD'], errors='coerce')
    df['OPENING TOTAL'] = pd.to_numeric(df['OPENING TOTAL'], errors='coerce')
    df['implied_team_total'] = (df['OPENING TOTAL'] / 2) - (df['OPENING SPREAD'] / 2)

    # Convert dates and sort chronologically
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values('DATE')
    
    # Calculate daily and cumulative league averages
    daily_avg = df.groupby('DATE').agg({
        'OEFF': 'mean',
        'DEFF': 'mean',
        'PACE': 'mean'
    }).rename(columns={
        'OEFF': 'daily_avg_oeff',
        'DEFF': 'daily_avg_deff',
        'PACE': 'daily_avg_pace'
    }).reset_index()
    
    daily_avg['cum_league_avg_oeff'] = daily_avg['daily_avg_oeff'].expanding().mean().shift(1)
    daily_avg['cum_league_avg_deff'] = daily_avg['daily_avg_deff'].expanding().mean().shift(1)
    daily_avg['cum_league_avg_pace'] = daily_avg['daily_avg_pace'].expanding().mean().shift(1)
    # Fill initial NaN (before day 1) with 0.0
    daily_avg['cum_league_avg_oeff'] = daily_avg['cum_league_avg_oeff'].fillna(0.0)
    daily_avg['cum_league_avg_deff'] = daily_avg['cum_league_avg_deff'].fillna(0.0)
    daily_avg['cum_league_avg_pace'] = daily_avg['cum_league_avg_pace'].fillna(0.0)
    
    df = pd.merge(df, daily_avg[['DATE', 'cum_league_avg_oeff', 'cum_league_avg_deff', 'cum_league_avg_pace']], on='DATE', how='left')
    
    # Calculate assist rate for each game
    df['ast_rate'] = df['A'] / df['FG']  # Assists per made field goal
    
    # Create a dictionary to track team stats cumulatively
    team_stats = {}
    
    # Initialize dictionary to store team stats
    for team in df['TEAM'].unique():
        team_stats[team] = {
            'oeff_sum': 0,
            'deff_sum': 0,
            'pace_sum': 0,
            'ast_sum': 0,
            'fg_sum': 0,
            'or_sum': 0,    # Offensive rebounds
            'dr_sum': 0,    # Defensive rebounds
            'opp_or_sum': 0, # Opponent offensive rebounds
            'opp_dr_sum': 0, # Opponent defensive rebounds
            'games': 0
        }
    
    # Add columns for team and opponent metrics
    df['team_avg_oeff'] = np.nan
    df['team_avg_deff'] = np.nan
    df['team_avg_pace'] = np.nan
    df['team_avg_ast_rate'] = np.nan
    df['team_avg_orr'] = np.nan
    df['team_avg_drr'] = np.nan
    df['opp_avg_oeff'] = np.nan
    df['opp_avg_deff'] = np.nan
    df['opp_avg_pace'] = np.nan
    df['opp_avg_orr'] = np.nan
    df['opp_avg_drr'] = np.nan
    df['adj_oeff'] = np.nan
    df['adj_deff'] = np.nan
    df['off_advantage'] = np.nan
    df['def_advantage'] = np.nan
    df['pace_diff'] = np.nan
    df['orr_advantage'] = np.nan
    df['drr_advantage'] = np.nan
    
    # Get first day league averages
    first_day = df['DATE'].min()
    first_day_oeff = df[df['DATE'] == first_day]['OEFF'].mean()
    first_day_deff = df[df['DATE'] == first_day]['DEFF'].mean()
    first_day_pace = df[df['DATE'] == first_day]['PACE'].mean()
    
    # FIRST PASS: Calculate rebounding rates
    game_opp_rebs = {}  # Store opponent rebound data by game_id and team
    
    for idx, row in df.iterrows():
        game_id = row['GAME-ID']
        team = row['TEAM']
        
        # Create a dictionary for this game if it doesn't exist
        if game_id not in game_opp_rebs:
            game_opp_rebs[game_id] = {}
        
        # Store this team's rebounds for opponents to use
        game_opp_rebs[game_id][team] = {
            'or': row['OR'],
            'dr': row['DR']
        }
    
    # Calculate rebounding rates for each game
    for idx, row in df.iterrows():
        game_id = row['GAME-ID']
        team = row['TEAM']
        
        # Find opponent
        opponent_rows = df[(df['GAME-ID'] == game_id) & (df['TEAM'] != team)]
        if len(opponent_rows) == 0:
            continue
            
        opponent = opponent_rows.iloc[0]['TEAM']
        
        # Get opponent rebounds
        opp_or = game_opp_rebs[game_id][opponent]['or']
        opp_dr = game_opp_rebs[game_id][opponent]['dr']
        
        # Calculate rebounding rates
        # Offensive rebound rate = OR / (OR + opponent DR)
        if (row['OR'] + opp_dr) > 0:
            df.at[idx, 'orr'] = row['OR'] / (row['OR'] + opp_dr)
        else:
            df.at[idx, 'orr'] = 0
        
        # Defensive rebound rate = DR / (DR + opponent OR)
        if (row['DR'] + opp_or) > 0:
            df.at[idx, 'drr'] = row['DR'] / (row['DR'] + opp_or)
        else:
            df.at[idx, 'drr'] = 0
    
    # SECOND PASS: Calculate team averages for all games
    for idx, row in df.iterrows():
        team = row['TEAM']
        
        # Calculate and store team averages before adding the current game
        if team_stats[team]['games'] > 0:
            df.at[idx, 'team_avg_oeff'] = team_stats[team]['oeff_sum'] / team_stats[team]['games']
            df.at[idx, 'team_avg_deff'] = team_stats[team]['deff_sum'] / team_stats[team]['games']
            df.at[idx, 'team_avg_pace'] = team_stats[team]['pace_sum'] / team_stats[team]['games']
            
            # Assist rate
            if team_stats[team]['fg_sum'] > 0:
                df.at[idx, 'team_avg_ast_rate'] = team_stats[team]['ast_sum'] / team_stats[team]['fg_sum']
            else:
                df.at[idx, 'team_avg_ast_rate'] = 0
                
            # Rebound rates
            if team_stats[team]['or_sum'] + team_stats[team]['opp_dr_sum'] > 0:
                df.at[idx, 'team_avg_orr'] = team_stats[team]['or_sum'] / (team_stats[team]['or_sum'] + team_stats[team]['opp_dr_sum'])
            else:
                df.at[idx, 'team_avg_orr'] = 0
                
            if team_stats[team]['dr_sum'] + team_stats[team]['opp_or_sum'] > 0:
                df.at[idx, 'team_avg_drr'] = team_stats[team]['dr_sum'] / (team_stats[team]['dr_sum'] + team_stats[team]['opp_or_sum'])
            else:
                df.at[idx, 'team_avg_drr'] = 0
        else:
            # For first game, use actual game values
                df.at[idx, 'team_avg_oeff'] = 0.0
                df.at[idx, 'team_avg_deff'] = 0.0
                df.at[idx, 'team_avg_pace'] = 0.0
                df.at[idx, 'team_avg_ast_rate'] = 0.0
                df.at[idx, 'team_avg_orr'] = 0.0
                df.at[idx, 'team_avg_drr'] = 0.0
        
        # Update team's cumulative stats for future games
        team_stats[team]['oeff_sum'] += row['OEFF']
        team_stats[team]['deff_sum'] += row['DEFF']
        team_stats[team]['pace_sum'] += row['PACE']
        team_stats[team]['ast_sum'] += row['A']
        team_stats[team]['fg_sum'] += row['FG']
        team_stats[team]['or_sum'] += row['OR']
        team_stats[team]['dr_sum'] += row['DR']
        
        # Update opponent rebound sums
        opponent_rows = df[(df['GAME-ID'] == row['GAME-ID']) & (df['TEAM'] != team)]
        if len(opponent_rows) > 0:
            opp_row = opponent_rows.iloc[0]
            team_stats[team]['opp_or_sum'] += opp_row['OR']
            team_stats[team]['opp_dr_sum'] += opp_row['DR']
        
        team_stats[team]['games'] += 1
    
    # THIRD PASS: Calculate opponent averages and adjusted metrics
    for idx, row in df.iterrows():
        game_id = row['GAME-ID']
        team = row['TEAM']
        
        team_avg_oeff = df.at[idx, 'team_avg_oeff'] # Team's avg O BEFORE this game
        team_avg_deff = df.at[idx, 'team_avg_deff']

        # Find opponent in this game
        opponent_row = df[(df['GAME-ID'] == game_id) & (df['TEAM'] != team)]
        if len(opponent_row) == 0:
            continue
            
        opponent = opponent_row.iloc[0]['TEAM']
        
        # Get opponent's team_avg values from their row for this game
        opp_idx = opponent_row.index[0]
        opp_avg_oeff = df.at[opp_idx, 'team_avg_oeff']
        opp_avg_deff = df.at[opp_idx, 'team_avg_deff']
        opp_avg_pace = df.at[opp_idx, 'team_avg_pace']
        opp_avg_orr = df.at[opp_idx, 'team_avg_orr']
        opp_avg_drr = df.at[opp_idx, 'team_avg_drr']
        
        # Store opponent averages
        df.at[idx, 'opp_avg_oeff'] = opp_avg_oeff
        df.at[idx, 'opp_avg_deff'] = opp_avg_deff
        df.at[idx, 'opp_avg_pace'] = opp_avg_pace
        df.at[idx, 'opp_avg_orr'] = opp_avg_orr
        df.at[idx, 'opp_avg_drr'] = opp_avg_drr
        
        # Calculate adjusted metrics
        league_avg_oeff = row['cum_league_avg_oeff']
        league_avg_deff = row['cum_league_avg_deff']
        
        df.at[idx, 'pred_adj_oeff'] = np.nan
        df.at[idx, 'pred_adj_deff'] = np.nan

        if pd.notna(team_avg_oeff) and pd.notna(opp_avg_deff) and pd.notna(league_avg_deff) and league_avg_deff != 0.0:
           # Main calculation
           df.at[idx, 'pred_adj_oeff'] = team_avg_oeff * (opp_avg_deff / league_avg_deff)
        elif pd.notna(team_avg_oeff):
            # Use incoming team average
            df.at[idx, 'pred_adj_oeff'] = team_avg_oeff

        if pd.notna(team_avg_deff) and pd.notna(opp_avg_oeff) and pd.notna(league_avg_oeff) and league_avg_oeff != 0.0:
           # Main calculation
           df.at[idx, 'pred_adj_deff'] = team_avg_deff * (opp_avg_oeff / league_avg_oeff)
        elif pd.notna(team_avg_deff):
           # Use incoming team average
           df.at[idx, 'pred_adj_deff'] = team_avg_deff
        
        # Calculate matchup advantage metrics
        team_oeff = team_avg_oeff
        team_deff = team_avg_deff
        team_pace = df.at[idx, 'team_avg_pace']
        team_orr = df.at[idx, 'team_avg_orr']
        team_drr = df.at[idx, 'team_avg_drr']

        opp_oeff = df.at[idx, 'opp_avg_oeff']
        opp_deff = df.at[idx, 'opp_avg_deff']
        opp_pace = df.at[idx, 'opp_avg_pace']
        opp_orr = df.at[idx, 'opp_avg_orr']
        opp_drr = df.at[idx, 'opp_avg_drr']

        # Calculate advantages, defaulting to 0.0 if either team has no prior data (avg is 0.0)
        if pd.isna(team_oeff) or team_oeff == 0.0 or pd.isna(opp_deff) or opp_deff == 0.0:
            df.at[idx, 'off_advantage'] = 0.0
        else:
            df.at[idx, 'off_advantage'] = team_oeff - opp_deff

        if pd.isna(opp_oeff) or opp_oeff == 0.0 or pd.isna(team_deff) or team_deff == 0.0:
            df.at[idx, 'def_advantage'] = 0.0
        else:
            df.at[idx, 'def_advantage'] = opp_oeff - team_deff 

        if pd.isna(team_pace) or team_pace == 0.0 or pd.isna(opp_pace) or opp_pace == 0.0:
            df.at[idx, 'pace_diff'] = 0.0
        else:
            df.at[idx, 'pace_diff'] = team_pace - opp_pace

        # For rebounding advantages, check if required opponent rate exists
        opp_drr_inv = (1.0 - opp_drr) if pd.notna(opp_drr) and opp_drr != 0.0 else 0.0
        if pd.isna(team_orr) or team_orr == 0.0 or opp_drr_inv == 0.0 :
             df.at[idx, 'orr_advantage'] = 0.0
        else:
             df.at[idx, 'orr_advantage'] = team_orr - opp_drr_inv # Team ORR vs Opponent non-DRR

        opp_orr_inv = (1.0 - opp_orr) if pd.notna(opp_orr) and opp_orr != 0.0 else 0.0
        if pd.isna(team_drr) or team_drr == 0.0 or opp_orr_inv == 0.0:
             df.at[idx, 'drr_advantage'] = 0.0
        else:
             df.at[idx, 'drr_advantage'] = team_drr - opp_orr_inv
    
    # Create a team season summary
    team_season = df.groupby('TEAM').agg({
        'OEFF': 'mean',                     # Raw average OEFF
        'DEFF': 'mean',                     # Raw average DEFF
        'pred_adj_oeff': 'mean',            # Average of the predictive adjusted OEFF
        'pred_adj_deff': 'mean',            # Average of the predictive adjusted DEFF
        'PACE': 'mean',
        'team_avg_ast_rate': 'mean',
        'team_avg_orr': 'mean',
        'team_avg_drr': 'mean'
    }).reset_index()

    # Calculate net ratings
    team_season['raw_net_rtg'] = team_season['OEFF'] - team_season['DEFF']
    team_season['pred_adj_net_rtg'] = team_season['pred_adj_oeff'] - team_season['pred_adj_deff']

    # Sort by predictive adjusted net rating
    team_season_sorted = team_season.sort_values('pred_adj_net_rtg', ascending=False)

    # Print team rankings
    print(f"\nTeam Rankings for {season} by Predictive Adjusted Net Rating:")
    print(team_season_sorted[['TEAM', 'pred_adj_oeff', 'pred_adj_deff', 'pred_adj_net_rtg']].head(10))
    
    # Save the processed data with the end year of the season
    output_file = os.path.join(output_dir, f"nba_{season_year}_team_metrics.csv")
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to: {output_file}")
    
    return team_season_sorted

def main():
    # Set up directories
    data_dir = '../../data'
    output_dir = os.path.join(data_dir, 'team_level_stats')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all NBA box score files directly from data directory
    box_score_files = glob.glob(os.path.join(data_dir, '*_NBA_Box_Score_Team-Stats.xlsx'))
    
    if not box_score_files:
        print(f"No NBA box score files found in {data_dir}")
        return
    
    print(f"Found {len(box_score_files)} NBA seasons to process")
    
    # Process each season
    for file_path in sorted(box_score_files):
        try:
            process_season(file_path, output_dir)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print("\nAll seasons processed successfully")

if __name__ == "__main__":
    main()