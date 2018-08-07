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
    logger.info('Build frequency model: SLM.')
    print(independents.columns, counts.head(), amounts.head())

    freq_model = sm.OLS(counts, independents)
    freq_results = freq_model.fit()
    freq_predictions = freq_results.predict(testing)
    _log_model_results(freq_results, 'slm_freq')

    logger.info('Build severity model: SLM.')
    sev_model = sm.OLS(amounts, independents)
    sev_results = sev_model.fit()
    sev_predictions = sev_results.predict(testing)
    _log_model_results(sev_results, 'slm_sev')

    res = pd.concat([freq_predictions, sev_predictions], axis=1)
    res.columns = ['E[N]', 'E[X]']
    return res


def evaluate_glm(independents: pd.DataFrame,
                 counts: pd.DataFrame,
                 amounts: pd.DataFrame,
                 testing: pd.DataFrame) -> pd.DataFrame:
    """
    Fit a statsmodel GLM using poisson for the frequency and gamma for
    severity.
    """
    logger.info('Build frequency model: GLM.')
    freq_model = sm.GLM(counts,
                        independents,
                        family=sm.families.Poisson(sm.families.links.log))
    freq_results = freq_model.fit()
    freq_predictions = freq_results.predict(testing)
    _log_model_results(freq_results, 'glm_freq')

    print(amounts.head())
    logger.info('Build severity model: GLM.')
    sev_model = sm.GLM(amounts,
                       independents,
                       family=sm.families.Gamma(sm.families.links.identity))
    sev_results = sev_model.fit()
    sev_predictions = sev_results.predict(testing)
    _log_model_results(sev_results, 'glm_sev')

    res = pd.concat([freq_predictions, sev_predictions], axis=1) 
    res.columns = ['E[N]', 'E[X]']
    return res


def _log_model_results(res: RegressionResults, name: str) -> None:
    """
    Store the results of a model fitting in a log file.
    """
    logger.info(f'Logging results of {name} model.')
    with open(f'{name}.log', 'w') as f:
        f.write(res.summary().as_text())
