from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer
import pandas as pd
import numpy as np

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, EXTERNAL_DATA_DIR

app = typer.Typer()


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = RAW_DATA_DIR / "dataset.csv",
    output_path: Path = PROCESSED_DATA_DIR / "dataset.csv",
    # ----------------------------------------------
):
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Processing dataset...")
    for i in tqdm(range(10), total=10):
        if i == 5:
            logger.info("Something happened for iteration 5.")
    logger.success("Processing dataset complete.")
    # -----------------------------------------

# Import raw data files
raw_data_files = ['ResaleFlatPricesBasedonApprovalDate19901999.csv',
                  'ResaleFlatPricesBasedonApprovalDate2000Feb2012.csv',
                  'ResaleFlatPricesBasedonRegistrationDateFromMar2012toDec2014.csv',
                  'ResaleFlatPricesBasedonRegistrationDateFromJan2015toDec2016.csv',
                  'ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv']

dfs = [pd.read_csv(RAW_DATA_DIR / file) for file in raw_data_files]
df = pd.concat(dfs, ignore_index=True)

# Data Cleaning
# Combining "MULTI-GENERATION" and "MULTI GENERATION" flat types
df['flat_type'] = df['flat_type'].replace({'MULTI GENERATION' : 'MULTI-GENERATION'})

# Creating a date column by setting the day from each month to 01 since the oriinal time format provided is has no day provided
df['date'] = pd.to_datetime(df['month'], format='%Y-%m')

# Creating a year column
df['year'] = df['date'].dt.strftime('%Y').astype('int64')

# Modifying the month column to display only months
df['month'] = df['date'].dt.strftime('%m').astype('int64')

# Adding a year_leased column
df['years_leased'] = df['year'] - df['lease_commence_date']

# Rearranging columns
df = df.loc[:, ['date', 'month', 'year', 'town', 'flat_type', 'block', 'street_name', 'storey_range', 'floor_area_sqm',
               'flat_model', 'lease_commence_date', 'years_leased', 'resale_price']]

# Changing flat model and town name to proper case
df['flat_model'] = df['flat_model'].apply(lambda x: x.title())
df['town'] = df['town'].apply(lambda x: x.title())

# Renaming the lease_commence_date to lease_year
df = df.rename({'lease_commence_date':'lease_year'}, axis=1)

# Adjusting prices for inflation
# Creating a dataframe for percent inflation figures in Singapore
infl = pd.read_csv(EXTERNAL_DATA_DIR / 'API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_77.csv')
infl = infl.loc[infl['Country Name'] == 'Singapore', '1990':]
infl = infl.rename({208:'infl'})

# Adding 2024 inflation as 0
infl['2024'] = 0

# Transposing the inflation dataframe
infl = infl.T

# Calculating cumulative inflation figures (2024)
infl['cum_infl'] = infl.iloc[::-1,:].cumsum()

# Resetting index, renaming the index column to 'year', and setting the dtype to int64
infl = infl.reset_index()
infl = infl.rename({'index':'year'}, axis=1)
infl['year'] = infl['year'].astype('int64')

# Merging the original dataframe with the inflation dataframe on year
df = pd.merge(df, infl[['year', 'cum_infl']], on='year', how='left')

# Adding a column for resale price adjusted by inflation
df['infl_adj_price'] = df['resale_price'] + df['resale_price']*df['cum_infl']/100
df['infl_adj_price'] = df['infl_adj_price'].round(1)
df = df.drop('cum_infl', axis=1)

# Save processed dataset
filename = 'ResaleFlatPrices-Processed.csv'
df.to_csv(PROCESSED_DATA_DIR / filename, index=False)

if __name__ == "__main__":
    app()
