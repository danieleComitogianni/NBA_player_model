import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)

# -------------------------
# Helper Functions
# -------------------------
def calc_moving_avg_1(df, columns, player_id_col):
    """
    Calculates the previous game’s value for the specified columns, grouped by player.
    """
    df = df.sort_values([player_id_col, 'date'])
    for col in columns:
        new_col = f'rolling_1_{col}'
        # Directly shift to get the previous game’s value
        df[new_col] = df.groupby(player_id_col)[col].shift(1)
        # Fill missing values with 0
        df[new_col] = df[new_col].fillna(0)
    return df

def calc_ewma_3(df, columns, player_id_col):
    """
    Calculates 3-game lagged moving averages for specified columns grouped by player.
    """
    df = df.sort_values([player_id_col, 'date'])
    for col in columns:
        new_col = f'ewma_3_{col}'
        df[new_col] = df.groupby(player_id_col)[col].transform(
            lambda x: x.ewm(span=3, min_periods=1, adjust=False).mean().shift(1)
        )
        # Fill missing values with 0
        df[new_col] = df[new_col].fillna(0)
    return df

def calc_ewma_5(df, columns, player_id_col):
    """
    Calculates 5-game lagged moving averages for specified columns grouped by player.
    """
    df = df.sort_values([player_id_col, 'date'])
    for col in columns:
        new_col = f'ewma_5_{col}'
        df[new_col] = df.groupby(player_id_col)[col].transform(
            lambda x: x.ewm(span=5, min_periods=1, adjust=False).mean().shift(1)
        )
        # Fill missing values with 0
        df[new_col] = df[new_col].fillna(0)
    return df

def calc_ewma_10(df, columns, player_id_col):
    """
    Calculates 10-game lagged moving averages for specified columns grouped by player.
    """
    df = df.sort_values([player_id_col, 'date'])
    for col in columns:
        new_col = f'ewma_10_{col}'
        df[new_col] = df.groupby(player_id_col)[col].transform(
            lambda x: x.ewm(span=10, min_periods=1, adjust=False).mean().shift(1)
        )
        # Fill missing values with 0
        df[new_col] = df[new_col].fillna(0)
    return df

def add_rolling_averages(df, col, windows=[1, 3, 5, 10], group_col=None):
    """Add lagged rolling averages for a given column across multiple window sizes."""
    if group_col is None:
        group_col = 'player_name'
    df = df.sort_values([group_col, 'date'])
    for window in windows:
        new_col = f'rolling_{window}_{col}'
        df[new_col] = df.groupby(group_col)[col].transform(
            lambda x: x.rolling(window, min_periods=1).mean().shift(1)
        )
        # Fill missing values with 0
        df[new_col] = df[new_col].fillna(0)
    return df

def add_ewma(df, col, windows=[3, 5, 10, 20], group_col=None):
    """Add exponential moving averages for a given column across multiple window sizes."""
    if group_col is None:
        group_col = 'player_name'
    df = df.sort_values([group_col, 'date'])
    for window in windows:
        new_col = f'ewma_{window}_{col}'
        df[new_col] = df.groupby(group_col)[col].transform(lambda x: x.ewm(span=window, min_periods=1, adjust=False).mean().shift(1))
        # Fill missing values with 0
        df[new_col] = df[new_col].fillna(0)
    return df

def add_season_average(df, columns, group_col):
    """Calculate player's season average at the instance of that time step."""
    df = df.sort_values([group_col, 'date'])
    for col in columns:
        season_avg_col = f'season_avg_{col}'
        df[season_avg_col] = df.groupby(group_col)[col].transform(
            lambda x: x.expanding(min_periods=1).mean().shift(1)
        )
        df[season_avg_col] = df[season_avg_col].fillna(0)
    return df


def process_season(year):
    print(f"Processing season {year}...")
    # Load the dataset for the given season
    file_path = f'../../data/processed_{year}.xlsx'
    df_orig = pd.read_excel(file_path)
    df_orig['date'] = pd.to_datetime(df_orig['date'])
    df = df_orig.copy()
    
    # Drop any unnamed columns
    unnamed_columns = [col for col in df.columns if 'Unnamed' in str(col)]
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0']).reset_index(drop=True)
    
    # Determine player identifier column
    if 'player_id' in df.columns and df['player_id'].dtype.name != 'str':
        player_id_col = 'player_id'
    else:
        player_id_col = 'player_name'
    
    # Replace the string rest days to numerical. Add a constraint for rest dys over 9 days to identify injuries or extended abscence
    if 'rest_days' in df.columns:
        # Convert '3+' to 3
        df['rest_days_numeric'] = df['rest_days'].replace('3+', 3).astype(float)
        df['extended_absence'] = (df['rest_days_numeric'] > 9).astype(int)
        df['is_b2b'] = (df['rest_days_numeric'] == 0).astype(int)
        df = df.drop(columns=['rest_days'])


    # Define the base stats columns
    base_stats = [
        'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 
        'OR', 'DR', 'TOT', 'A', 'ST', 'BL', 'TO', 'PF', 'PTS', 'MIN','usage_rate(%)'
    ]
    
    # Calculate lagged moving averages for base stats
    df = calc_moving_avg_1(df, base_stats, player_id_col)
    df = calc_ewma_3(df, base_stats, player_id_col)
    df = calc_ewma_5(df, base_stats, player_id_col)
    df = calc_ewma_10(df, base_stats, player_id_col)
    
    # FEATURE ENGINEERING: Deriving additional statistics from base stats
    df['FG%'] = np.where(df['FGA'] > 0, df['FG'] / df['FGA'], 0)
    df['3P%'] = np.where(df['3PA'] > 0, df['3P'] / df['3PA'], 0)
    df['eFG%'] = np.where(df['FGA'] > 0, (df['FG'] + 0.5 * df['3P']) / df['FGA'], 0)
    df['TS%'] = np.where((df['FGA'] + 0.44 * df['FTA']) > 0,
                         0.5 * df['PTS'] / (df['FGA'] + 0.44 * df['FTA']),
                         0)
    df['TSA'] = df['FGA'] + 0.44 * df['FTA']
    df['PTS_per36'] = np.where(df['MIN'] > 0, (36 * df['PTS']) / df['MIN'], 0)
    df['TOT_per36'] = np.where(df['MIN'] > 0, (36 * df['TOT']) / df['MIN'], 0)
    df['A_per36'] = np.where(df['MIN'] > 0, (36 * df['A']) / df['MIN'], 0)
    df['GmSc'] = (
        df['PTS'] +
        0.4 * df['FG'] -
        0.7 * df['FGA'] -
        0.4 * (df['FTA'] - df['FT']) +
        0.7 * df['OR'] +
        0.3 * df['DR'] +
        df['ST'] +
        0.7 * df['A'] +
        0.7 * df['BL'] -
        0.4 * df['PF'] -
        df['TO']
    )
    
    # Calculate lagged rolling averages for derived features
    derived_features = ['FG%', '3P%', 'eFG%', 'TS%', 'TSA', 'PTS_per36', 'TOT_per36', 'A_per36', 'GmSc']
    for feat in derived_features:
        df = add_rolling_averages(df, feat, windows=[1], group_col=player_id_col)
        df = add_ewma(df, feat, windows=[3, 5, 10, 20], group_col=player_id_col)
    
    # Calculate season averages and differences
    avg_features = ['MIN', 'PTS', 'FG%', '3P%', 'eFG%', 'TS%', 'TSA', 'BL', 'A', 'TO', 'GmSc', 'OR', 'DR', 'TOT']
    df = add_season_average(df, avg_features, player_id_col)
    
    # Identify new columns to merge back into the original dataframe
    new_cols = [c for c in df.columns if c not in df_orig.columns]
    join_keys = ['game_id', player_id_col]
    
    merged_df = df_orig.merge(df[join_keys + new_cols], on=join_keys, how='left')
    
    print(f"Original columns: {len(df_orig.columns)}")
    print(f"New columns added: {len(new_cols)}")
    print(f"Total columns: {len(merged_df.columns)}")
    
    # Save the preprocessed dataset for the current season
    output_file = f'../../data/feature_engineer/feature_engineered_{year}.xlsx'
    merged_df.to_excel(output_file, index=False)
    print(f"Saved processed file to {output_file}\n")
    df.head(1)

for year in range(2015, 2025):
    process_season(year)
