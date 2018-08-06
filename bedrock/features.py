import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a dataframe of policies, modify and produce the data to form
    the desired set of feature columns.
    """
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
