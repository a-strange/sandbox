import io
import json
import os
import pickle
from typing import Dict

import pandas as pd

from google.cloud import storage

CONFIG_PATH = 'config.json'

SOURCE_PATH = 'bedrock'
SOURCE_FILES = {
    'policies': 'train_policies.pkl',
    'claims': 'train_claims.pkl',
    'test': 'test_policies.pkl'
}


def _load_config() -> Dict[str, str]:
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def get_pickle_file(path: str,
                    client: storage.Client,
                    bucket: str) -> pd.DataFrame:
    """
    Retrieve a pickle file from the target GCS bucket and convert to
    DataFrame.
    """
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(path)
    df_io = io.BytesIO()
    blob.download_to_file(df_io)
    df_io.seek(0)
    df = pickle.load(df_io)
    df_io.close()
    return df


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
    policies = get_pickle_file(os.path.join(SOURCE_PATH,
                                            SOURCE_FILES['policies']),
                               client,
                               config['bucket'])
    print(policies.head())


if __name__ == '__main__':
    main()
