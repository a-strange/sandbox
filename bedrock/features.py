import logging
from typing import Tuple

import pandas as pd

logger = logging.getLogger(__name__)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a dataframe of policies, modify and produce the data to form
    the desired set of feature columns.
    """
    drop_cols = {'insured', 'trade'}

    # Convert year variable to int. Formatting year like this was mean.
    df['year_built'] = (df['year_built']
                        .str.extract(r'year\:([0-9]{4})')
                        .astype(int))

    # Convert sprinklers to binary variable.
    df['sprinklers'] = df['sprinklers'].map({'Yes': 1, 'No': 0})

    # Convert categorical trade column to binary flags.
    df = convert_categorical_column(df, 'trade')
    df.set_index('pol_id')

    feature_cols = set(df.columns)
    return df[list(feature_cols.difference(drop_cols))]


def convert_categorical_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Convert a categorical column into a set of binary flag columns.
    """
    categories = df[col].unique()
    for cat in categories:
        df[f'{col}_{cat}'] = pd.np.where(df[col] == cat, 1, 0)
    return df


def get_claim_counts(policies: pd.DataFrame,
                     grouped_claims: pd.core.groupby.GroupBy) -> pd.Series:
    """
    Compute claim count per policy.
    """
    logger.info('Calculate claim counts.')
    counts = grouped_claims['claim_id'].count()
    counts = policies.join(counts, on='pol_id')
    counts = counts.drop_duplicates('pol_id')['claim_id']
    counts.fillna(0, inplace=True)
    return counts


def get_claim_amounts(policies: pd.DataFrame,
                      grouped_claims: pd.core.groupby.GroupBy) -> Tuple[pd.Series, pd.Series]:
    logger.info('Calculate claim amounts')
    totals = grouped_claims['claim_amount'].sum()
    averages = totals / grouped_claims['claim_amount'].count()

    totals = policies.join(totals)
    totals = totals[~totals.index.duplicated(keep='first')]['claim_amount']
    totals.fillna(0.0, inplace=True)

    averages = policies.join(averages)
    averages = averages[
        ~averages.index.duplicated(keep='first')
    ]['claim_amount']
    averages.fillna(0.0, inplace=True)

    return totals, averages
