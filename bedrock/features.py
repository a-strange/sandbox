from typing import Tuple

import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a dataframe of policies, modify and produce the data to form
    the desired set of feature columns.
    """
    # Convert year variable to int. Formatting year like this was mean.
    df['year_built'] = (df['year_built']
                        .str.extract(r'year\:([0-9]{4})')
                        .astype(int))

    # Convert sprinklers to binary variable.
    df['sprinklers'] = df['sprinklers'].map({'Yes': 1, 'No': 0})

    # Convert categorical trade column to binary flags.
    df = convert_categorical_column(df, 'trade')


def convert_categorical_column(df: pd.DateFrame, col: str) -> pd.DataFrame:
    """
    Convert a categorical column into a set of binary flag columns.
    """
    categories = df[col].unique()
    for cat in categories:
        df[f'{col}_{cat}'] = pd.np.where(df[col] == cat, 1, 0)
    return df


def get_claim_counts(policies: pd.DataFrame,
                     grouped_claims: pd.DataFrameGroupBy) -> pd.Series:
    """
    Compute claim count per policy.
    """
    return grouped_claims.count()
    """
    counts = policies.join(counts, on='pol_id', r_suffix='_r')['pol_id_r']
    counts.fillna(0.0)
    """


def get_claim_amounts(policies: pd.DataFrame,
                      grouped_claims: pd.DataFrameGroupBy) -> Tuple[pd.Series, pd.Series]:
    totals = grouped_claims['claim_amount'].sum()
    averages = totals / grouped_claims['claim_amount'].count()

    totals = policies.join(totals,
                           on='pol_id',
                           r_suffix='_r')['claim_amount_r']
    totals.fillna(0.0, inplace=True)

    averages = policies.join(averages,
                             on='pol_id',
                             r_suffix='_r')['claim_amount_r']
    averages.fillna(0.0, inplace=True)

    return totals, averages
