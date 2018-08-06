import io
import json
import os
import pickle
from typing import Dict

from google.cloud import storage
import pandas as pd
import pkg_resources

from features import build_features, get_claim_amounts, get_claim_counts

CONFIG_PATH = 'config.json'

SOURCE_PATH = 'bedrock'
SOURCE_FILES = {
    'policies': 'train_policies.pkl',
    'claims': 'train_claims.pkl',
    'test': 'test_policies.pkl'
}


def _load_config() -> Dict[str, str]:
    path = pkg_resources(__name__, CONFIG_PATH)
    with open(path, 'r') as f:
        return json.load(f)


def _get_pickle_file(path: str,
                     client: storage.Client,
                     bucket: str) -> pd.DataFrame:
    """
    Retrieve a pickle file from the target GCS bucket and convert to
    DataFrame.
    """
    path = os.path.join(SOURCE_PATH, path)
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(path)
    df_io = io.BytesIO()
    blob.download_to_file(df_io)
    df_io.seek(0)
    df = pickle.load(df_io)
    df_io.close()
    return df


def run_models(policies: pd.DataFrame,
               claims: pd.DataFrame,
               test: pd.DataFrame,
               config: Dict[str, str]) -> None:
    """
    With the loaded datasets, run the complete process of model building
    for each of SLM, GLM and MLM.
    """
    policies = build_features(policies)
    averages, totals = get_claim_amounts(policies, claims)
    counts = get_claim_counts(policies, claims)
    print(policies.head(), averages.head(), totals.head(), counts.head())


def main() -> None:
    """
    Download and extract the three pickle files.
    For each of:
        SLM,
        GLM,
        MLM,
            Convert files to format for building and eval of model,
                May be shared logic/objects
            Build model as required,
            Calculate predictions on test Data
            Store results on GCS/GDrive
    """
    config = _load_config()
    client = storage.Client(project=config['project'])

    policies = _get_pickle_file(SOURCE_FILES['policies'],
                                client,
                                config['bucket'])
    claims = _get_pickle_file(SOURCE_FILES['claims'],
                              client,
                              config['bucket'])
    test = _get_pickle_file(SOURCE_FILES['test'],
                            client,
                            config['bucket'])

    run_models(policies, claims, test, config)


if __name__ == '__main__':
    main()
