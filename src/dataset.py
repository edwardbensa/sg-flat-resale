from pathlib import Path
import typer
import pandas as pd
import geopandas as gpd

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
    df['month'] = df['date'].dt.month
    df = df.rename(columns={'lease_commence_date': 'lease_year'})
    df['years_leased'] = df['year'] - df['lease_year']
    df = df[df['years_leased']>=0]

    # Set entries to proper case
    for col in ['town', 'street_name', 'flat_model', 'flat_type']:
        df[col] = df[col].str.title()
    df['street_name'] = df['street_name'].replace({"'S":"'s"}, regex=True)

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
    infl = infl.rename({208:'inflation%'})
    infl['2024'] = 2.389511236
    infl = infl.T
    infl['point_index'] = infl['inflation%'].apply(lambda a: 1+a/100)
    infl['cum_index'] = infl['point_index'].iloc[::-1].cumprod()
    infl = infl.reset_index()
    infl = infl.rename({'index':'year'}, axis=1)
    infl['year'] = infl['year'].astype('int64')

    df = df.merge(infl[['year', 'cum_index']], on='year', how='left')
    df['infl_adj_price'] = df['resale_price']*df['cum_index']
    df['infl_adj_price'] = df['infl_adj_price'].round(1)
    df.drop(columns='cum_index', inplace=True)
    logger.info("Inflation-adjusted prices calculated.")

    # Geospatial
    # Add planning_area column
    df['planning_area'] = df['town']

    # Modify planning_area entries for town == Central Area and town == Kallang/Whampoa
    town_mappings = {
        "Central Area": {
            "Outram": ["Outram", "Smith St", "Jln Kukoh", "Sago Lane", "New Mkt Rd", 
                    "Upp Cross St", "Chin Swee Rd", "Kreta Ayer Rd", "Cantonment Rd"],
            "Rochor": ["Queen", "Rowell", "Rochor", "Bain St", "Short St", "Jln Berseh", 
                    "Selegie Rd", "Buffalo Rd", "Chander Rd", "Klang Lane", "Kelantan Rd", 
                    "Waterloo St", "Veerasamy Rd"],
            "Bukit Merah": ["Tg Pagar Plaza"]
        },
        "Kallang/Whampoa": {
            "Novena": ["Whampoa", "Kent Rd", "Jln Rajah", "Lor Limau", "Jln Dusun", 
                    "Ah Hood Rd", "Moulmein Rd", "Jln Bahagia", "Jln Tenteram", "Gloucester Rd"],
            "Kallang": ["Owen Rd", "Jln Batu", "Mcnair Rd", "Towner Rd", "Dorset Rd", "French Rd",
                        "Jln Ma'Mor", "Kg Kayu Rd", "Kg Arang Rd", "Jellicoe Rd", "Lor 3 Geylang",
                        "Tessensohn Rd", "Farrer Pk Rd", "Boon Keng Rd", "Bendemeer Rd", "Cambridge Rd",
                        "Crawford Lane", "Nth Bridge Rd", "Geylang Bahru", "Kallang Bahru", "Race Course Rd",
                        "St. George's Rd", "Upp Boon Keng Rd", "St. George's Lane", "King George's Ave"]
        }
    }

    # Apply street mappings with town filter
    def apply_street_mappings(df, mappings):
        for town, areas in mappings.items():
            town_mask = df['town'] == town
            for area, streets in areas.items():
                pattern = '|'.join(streets)
                street_mask = df['street_name'].str.contains(pattern, case=False, na=False)
                df.loc[town_mask & street_mask, 'planning_area'] = area

    apply_street_mappings(df, town_mappings)

    # Handle specific block mappings
    beach_rd_blocks = {
        'Rochor': ['1', '2', '3', '6'],
        'Kallang': ['15', '17']
    }

    beach_rd_mask = (df['town'] == 'Kallang/Whampoa') & (df['street_name'] == 'Beach Rd')
    for area, blocks in beach_rd_blocks.items():
        block_pattern = '|'.join(blocks)
        df.loc[beach_rd_mask & df['block'].str.contains(block_pattern, case=False, na=False), 'planning_area'] = area

    logger.info("Added planning area data.")

    # Export
    df.to_csv(output_path, index=False)
    logger.success(f"Dataset saved to: {output_path}")

if __name__ == "__main__":
    app()
