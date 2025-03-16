import pandas as pd

darko_df = pd.read_excel('../../data/DARKO.xlsx')

#OK i have the dataframe for darko, now I want to filter the dataframe so it removes every instance under 2014
filtered_darko_df = darko_df[darko_df['season']>=2014]
filtered_darko_df = filtered_darko_df[filtered_darko_df['season']<2025]
#okay now I have the years 2014 to 2024 for darko, now Its time to merge wi
