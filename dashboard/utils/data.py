import pandas as pd

from src.config import PROCESSED_DATA_DIR
from src.utils.misc import bin_numbers


# Import and load cleaned data
filename = PROCESSED_DATA_DIR / 'ResaleFlatPrices-Processed.csv'
df = pd.read_csv(PROCESSED_DATA_DIR / filename)
df['date'] = pd.to_datetime(df['date'])

# Create copy of main dataframe for plotting purposes
df_p = df.copy()
df_p['year_binned'] = df_p['year'].apply(lambda a: bin_numbers(a, 1990, 10))
df_p['lease_year_binned'] = df_p['lease_year'].apply(lambda a: bin_numbers(a, 1960, 10))
df_p['years_leased_binned'] = df_p['years_leased'].apply(lambda a: bin_numbers(a, 0, 10))
df_p['start_floor_binned'] = df_p['start_floor'].apply(lambda a: bin_numbers(a, 1, 10))
df_p['quarter'] = df_p['month'].apply(lambda a: bin_numbers(a, 1, 3))
df_p['quarter'] = df_p['quarter'].replace({'1-3': 'Q1', '4-6': 'Q2', '7-9': 'Q3', '10-12': 'Q4',})

# Set x features for plotting
x_vars = ['year', 'lease_year', 'years_leased', 'month']