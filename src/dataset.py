from pathlib import Path
import typer
import pandas as pd

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, EXTERNAL_DATA_DIR
from src.utils.logging import setup_logger

app = typer.Typer()
logger = setup_logger()

@app.command()
def main(
    output_path: Path = PROCESSED_DATA_DIR / 'ResaleFlatPrices-Processed.csv',
):
    '''Imports and cleans data'''
    logger.info("Starting data processing...")

    # Import and concatenate raw datasets
    raw_files = [
        'ResaleFlatPricesBasedonApprovalDate19901999.csv',
        'ResaleFlatPricesBasedonApprovalDate2000Feb2012.csv',
        'ResaleFlatPricesBasedonRegistrationDateFromMar2012toDec2014.csv',
        'ResaleFlatPricesBasedonRegistrationDateFromJan2015toDec2016.csv',
        'ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv'
    ]
    dfs = [pd.read_csv(RAW_DATA_DIR / file) for file in raw_files]
    df = pd.concat(dfs, ignore_index=True)
    logger.info("Loaded and merged raw datasets.")

    # Data cleaning and formatting
    df['flat_type'] = df['flat_type'].replace({'MULTI GENERATION': 'MULTI-GENERATION'})
    df['date'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['year'] = df['date'].dt.year
    df = df.rename(columns={'lease_commence_date': 'lease_year'})
    df['years_leased'] = df['year'] - df['lease_year']
    df['town'] = df['town'].replace({'KALLANG/WHAMPOA': 'KALLANG'})

    # Set entries to proper case
    for col in ['town', 'street_name', 'flat_model', 'flat_type']:
        df[col] = df[col].str.title()

    # Storey range handling
    df[['start_floor', 'end_floor']] = df['storey_range'].str.extract(r'(\d+)\s+TO\s+(\d+)').astype(int)
    df['storey_count'] = df['end_floor'] - df['start_floor']

    # Reorder columns
    df = df[[
        'date', 'year', 'month', 'town', 'street_name', 'block', 'flat_type', 'flat_model',
        'storey_count', 'start_floor', 'floor_area_sqm', 'lease_year',
        'years_leased', 'resale_price'
    ]]
    logger.info("Cleaned and structured data.")

    # Inflation adjustment
    infl = pd.read_csv(EXTERNAL_DATA_DIR / 'API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_77.csv')
    infl = infl.loc[infl['Country Name'] == 'Singapore', '1990':]
    infl['2024'] = 0
    infl = infl.T
    infl['cum_infl'] = infl.iloc[::-1].cumsum()
    infl = infl.reset_index().rename(columns={'index': 'year'})
    infl['year'] = infl['year'].astype(int)

    df = df.merge(infl[['year', 'cum_infl']], on='year', how='left')
    df['infl_adj_price'] = df['resale_price'] * (1 + df['cum_infl'] / 100)
    df['infl_adj_price'] = df['infl_adj_price'].round(1)
    df.drop(columns='cum_infl', inplace=True)
    logger.info("Inflation-adjusted prices calculated.")

    # Export
    df.to_csv(output_path, index=False)
    logger.success(f"Dataset saved to: {output_path}")

if __name__ == "__main__":
    app()
