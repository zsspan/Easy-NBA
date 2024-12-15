"""
Module with various utility functions for cleaning and reformatting
given data.
"""

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

def convert_type(df: pd.DataFrame) -> pd.DataFrame:
    # define the numerical columns you want to convert
    numerical_columns = ["G", "PTS", "TRB", "AST", "STL", "BLK", "FG%", "FT%", "3P%", "TOV", 'MP']
    # df = df.copy()
    
    for col in numerical_columns:
        if col in df.columns:  # check if the column exists
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["STL", "BLK", "3P%", "FG%", "FT%", "TOV"]:
        if col not in df.columns:
            df[col] = -1

    # df.fillna(-1, inplace=True)  # ensure no NaN values remain in numeric columns

    return df

def clean_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    # create boolean Series
    has_yrs = df['Season'].str.contains('Yr', case=False, na=False)
    yrs_indices = df[has_yrs].index.tolist()
    agg_count = 1

    for i in yrs_indices:
        # entire career case
        if '(' not in df.at[i, 'Season']:
            df.at[i, 'Season'] = 'Career'
        # one team case
        else:
            team = df.at[i, 'Season']
            pos = team.find('(')
            df.at[i, 'Season'] = team[:pos]
            df.at[i, 'Team'] = np.nan

        df.rename(index={i: f"TOT_{agg_count}"}, inplace=True)
        agg_count += 1
    
def clean_fill(df: pd.DataFrame):
    df.replace(r"^Did not play.*", "-", regex=True, inplace=True)
    df.fillna(-1, inplace=True) # need to fix later
    df['G'] = df['G'].astype(int) # need to fix later
    
def clean_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df # must fix later
    
    df = convert_type(df)
    columns_to_drop = ['Age', 'Lg', 'GS', 'FGA', 'FG', '3P', '3PA', '2P', '2PA', '2P%', 
                   'eFG%', 'FT', 'FTA', 'ORB', 'DRB', 'PF', 'Awards']

    existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(existing_columns_to_drop, axis=1)
    
    # fixing NaN values and changing indices
    df.replace(-1, np.nan, inplace=True)
    df = df.dropna(axis=0, how='all')
    df.index = range(1, len(df) + 1)
    clean_aggregates(df)
    clean_fill(df)

    # print("REG:", df)
    df = df[df['Pos'] != 'Pos']

    return df

def front_end_clean(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    
    df.replace({"-1": '-', -1: '-'}, inplace=True)

    columns_to_drop = ['TOV', 'FT%', '3P%', 'MP']
    
    # drop extra stats in the df
    for col in columns_to_drop:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)

    return df

        