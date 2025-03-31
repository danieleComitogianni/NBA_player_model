import pandas as pd

pd.set_option('display.max_columns', None)
df2015 = pd.read_excel('../../data/final_final_data/final_final_2015.xlsx',index_col=0)
df2016 = pd.read_excel('../../data/final_final_data/final_final_2016.xlsx',index_col=0)
df2017 = pd.read_excel('../../data/final_final_data/final_final_2017.xlsx',index_col=0)
df2018 = pd.read_excel('../../data/final_final_data/final_final_2018.xlsx',index_col=0)
df2019 = pd.read_excel('../../data/final_final_data/final_final_2019.xlsx',index_col=0)
df2020 = pd.read_excel('../../data/final_final_data/final_final_2020.xlsx',index_col=0)
df2021 = pd.read_excel('../../data/final_final_data/final_final_2021.xlsx',index_col=0)
df2022 = pd.read_excel('../../data/final_final_data/final_final_2022.xlsx',index_col=0)
df2023 = pd.read_excel('../../data/final_final_data/final_final_2023.xlsx',index_col=0)
df2024 = pd.read_excel('../../data/final_final_data/final_final_2024.xlsx',index_col=0)

dfs = [df2024, df2023, df2022, df2021,df2020,df2019,df2018,df2017,df2016,df2015]
reference = set(dfs[0].columns)
for i, df in enumerate(dfs[1:], start=1):
    diff = reference.symmetric_difference(set(df.columns))
    if diff:
        print(f"Differences found in DataFrame {i}: {diff}")
    else:
        print(f"DataFrame {i} columns match the reference.")


merged_df = pd.concat([df2015,df2016,df2017,df2018,df2019,df2020,df2021,df2022,df2023,df2024], ignore_index=True)



pairs = [
    ("06/16/2015", 203925),
    ("10/27/2015", 202694),
    ("06/19/2016", 201578),
    ("10/25/2016", 2546),
    ("06/12/2017", 2561),
    ("10/17/2017", 202330),
    ("06/08/2018", 1627790),
    ("10/16/2018", 203967),
    ("06/13/2019", 201973),
    ("10/22/2019", 201950),
    ("10/11/2020", 1627884),
    ("12/22/2020", 203952),
    ("07/20/2021", 201952),
    ("10/19/2021", 201142),
    ("06/16/2022", 1629752),
    ("10/18/2022", 202699),
    ("06/12/2023", 201599),
    ("10/24/2023", 1627752),
    ("06/17/2024", 1629004),
]

pairs = [(pd.to_datetime(date_str, format='%m/%d/%Y'), player_id) for date_str, player_id in pairs]

for date_val, player in pairs:
    idx = merged_df[(merged_df['date'] == date_val) & (merged_df['player_id'] == player)].index
    print(f"Date: {date_val.date()}, Player ID: {player} -> Index: {idx.tolist()}")

merged_df.to_excel('../../data/merged_data_for_model/merged_model_data.xlsx')