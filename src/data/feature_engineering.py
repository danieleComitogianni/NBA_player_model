import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)

df_orig = pd.read_excel('../../data/processed_2015.xlsx')
df_orig['date'] = pd.to_datetime(df_orig['date'])

df = df_orig.copy()

def calc_moving_avg_3(df, columns):
    """
    Calculates 3-game moving averages for specified columns grouped by player.
    """
    # Ensure the DataFrame is sorted by player and date
    df = df.sort_values(['player_name', 'date'])
    for col in columns:
        new_col = f'rolling_3_{col}'
        df[new_col] = df.groupby('player_name')[col].transform(lambda x: x.rolling(window=3, min_periods=1).mean())
    return df

def calc_moving_avg_5(df, columns):
    """
    Calculates 5-game moving averages for specified columns grouped by player.
    """
    # Ensure the DataFrame is sorted by player and date
    df = df.sort_values(['player_name', 'date'])
    for col in columns:
        new_col = f'rolling_5_{col}'
        df[new_col] = df.groupby('player_name')[col].transform(lambda x: x.rolling(window=5, min_periods=1).mean())
    return df

def calc_moving_avg_10(df, columns):
    """
    Calculates 10-game moving averages for specified columns grouped by player.
    """
    # Ensure the DataFrame is sorted by player and date
    df = df.sort_values(['player_name', 'date'])
    for col in columns:
        new_col = f'rolling_10_{col}'
        df[new_col] = df.groupby('player_name')[col].transform(lambda x: x.rolling(window=10, min_periods=1).mean())
    return df


# Convert 'date' to datetime if not already
df['date'] = pd.to_datetime(df['date'])

# Define the rebound columns (Offensive, Defensive, Total Rebounds)
rebound_cols = ['OR', 'DR', 'TOT']

# Calculate 3, 5, and 10-game moving averages
df = calc_moving_avg_3(df, rebound_cols)
df = calc_moving_avg_5(df, rebound_cols)
df = calc_moving_avg_10(df, rebound_cols)

"""FEATURE ENGINEERING / DERIVING STATISTICS FROM BASELINE STATS"""
# field goal percentage
df['FG%'] = np.where(df['FGA'] > 0, df['FG'] / df['FGA'], 0)
# 3 pointer percentage
df['3P%'] = np.where(df['3PA'] > 0, df['3P'] / df['3PA'], 0)
# effective field goal percentage (shooting 3/4 3pointers is worth more than 3/4 2pointers)
df['eFG%'] = np.where(df['FGA'] > 0, (df['FG'] + 0.5 * df['3P']) / df['FGA'],0)
# true shooting percentage 
df['TS%'] = np.where((df['FGA'] + 0.44 * df['FTA']) > 0, 0.5 * df['PTS'] / (df['FGA'] + 0.44 * df['FTA']), 0)
# true shooting attempts
df['TSA'] = df['FGA'] + 0.44 * df['FTA']
# points, rebounds, assists per 36 minutes
df['PTS_per36'] = np.where(df['MIN'] > 0, (36 * df['PTS']) / df['MIN'], 0)
df['TOT_per36'] = np.where(df['MIN'] > 0, (36 * df['TOT']) / df['MIN'], 0)
df['A_per36']   = np.where(df['MIN'] > 0, (36 * df['A']) / df['MIN'], 0)
# gmsc = pts + 0.4*fg - 0.7*fga - 0.4*(fta - ft) + 0.7*or + 0.3*dr + stl + 0.7*a + 0.7*blk - 0.4*pf - to
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

def add_rolling_averages(df, col, windows=[3, 5, 10], group_col='player_name'):

    df = df.sort_values([group_col, 'date'])
    for window in windows:
        new_col = f'rolling_{window}_{col}'
        df[new_col] = df.groupby(group_col)[col].transform(lambda x: x.rolling(window, min_periods=1).mean())
    return df

features = ['FG%', '3P%', 'eFG%', 'TS%', 'TSA', 'PTS_per36', 'TOT_per36', 'A_per36', 'GmSc']

for feat in features:
    df = add_rolling_averages(df, feat, windows=[3, 5, 10], group_col='player_name')

new_cols = [c for c in df.columns if c not in df_orig.columns]

merged_df = df_orig.merge(
    df[['game_id','player_id'] + new_cols],
    on=['game_id','player_id'],
    how='left'
)

merged_df.to_excel('../../data/feature_engineered_2015.xlsx', index=False)
print(merged_df.info())
print(df_orig.info())


