import io
import json
import logging
import pickle
from typing import Dict

from google.cloud import storage
import pandas as pd
import pkg_resources

from features import build_features, get_claim_amounts, get_claim_counts
from models import evaluate_glm, evaluate_slm

CONFIG_PATH = 'config.json'

SOURCE_PATH = 'bedrock'
SOURCE_FILES = {
    'policies': 'train_policies.pkl',
    'claims': 'train_claims.pkl',
    'test': 'test_policies.pkl'
}
SUBMISSION_PATH = 'submissions'
SUBMISSION_FILES = {
    'slm': 'astrange-LM-01Vanilla.pkl',
    'glm': 'astrange-GLM-01Vanilla.pkl',
    'mlm': 'astrange-ML-01Vanilla.pkl'
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
)
logger = logging.getLogger(__name__)


def _load_config() -> Dict[str, str]:
    path = pkg_resources.resource_filename(__name__, CONFIG_PATH)
    with open(path, 'r') as f:
        return json.load(f)


def _get_pickle_file(path: str,
                     client: storage.Client,
                     bucket: str) -> pd.DataFrame:
    """
    Retrieve a pickle file from the target GCS bucket and convert to
    DataFrame.
    """
    logger.info(f'Download {path}')
    path = '/'.join([SOURCE_PATH, path])
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(path)
    df_io = io.BytesIO()
    blob.download_to_file(df_io)
    df_io.seek(0)
    df = pickle.load(df_io)
    df_io.close()
    return df


def _store_pickle_file(df: pd.DataFrame,
                       name: str,
                       client: storage.Client,
                       bucket: str) -> None:
    logger.info(f'Upload {name}')
    filename = SUBMISSION_FILES.get(name)
    path = '/'.join([SOURCE_PATH, SUBMISSION_PATH, filename])
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(path)
    df_io = io.BytesIO()
    pickle.dump(df, df_io)
    df_io.seek(0)
    blob.upload_from_file(df_io)
    df_io.close()


def run_models(policies: pd.DataFrame,
               claims: pd.DataFrame,
               testing: pd.DataFrame,
               config: Dict[str, str]) -> None:
    """
    With the loaded datasets, run the complete process of model building
    for each of SLM, GLM and MLM.
    """
    logging.info('Build features.')
    policies = build_features(policies)
    testing = build_features(testing)
    grouped = claims.groupby('pol_id')

    # Currently compute both averages and totals.
    averages, totals = get_claim_amounts(policies, grouped)
    counts = get_claim_counts(policies, grouped)

    res_slm = evaluate_slm(policies, counts, averages, testing)
    res_glm = evaluate_glm(policies, counts, averages, testing)

    client = storage.Client(project=config['project'])
    _store_pickle_file(res_slm, 'slm', client, config['bucket'])
    _store_pickle_file(res_glm, 'glm', client, config['bucket'])

    res_slm.to_csv('slm.csv', encoding='utf-8')
    res_glm.to_csv('slm.csv', encoding='utf-8')


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
