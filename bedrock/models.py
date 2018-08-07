import logging

import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.linear_model import RegressionResults

logger = logging.getLogger(__name__)


def evaluate_slm(independents: pd.DataFrame,
                 counts: pd.DataFrame,
                 amounts: pd.DataFrame,
                 testing: pd.DataFrame) -> pd.DataFrame:
    """
    Fit a simple linear model, evaluate on the testing data and return
    the predictions.
    """

    freq_model = sm.OLS(counts, independents)
    freq_results = freq_model.fit()
    freq_predictions = freq_results.predict(testing)
    _log_model_results(freq_results, 'slm_freq')

    sev_model = sm.OLS(amounts, independents)
    sev_results = sev_model.fit()
    sev_predictions = sev_results.predict(testing)
    _log_model_results(sev_results, 'slm_sev')

    res = freq_predictions.join(sev_predictions)
    res.columns = ['E[N]', 'E[X]']
    return res


def _log_model_results(res: RegressionResults, name: str) -> None:
    """
    Store the results of a model fitting in a log file.
    """
    logger.info(f'Logging results of {name} model.')
    with open(f'{name}.log', 'r') as f:
        f.write(res.summary())
