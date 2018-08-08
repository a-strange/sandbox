import logging
from multiprocessing import Pool
from typing import Tuple, Union

import pandas as pd
import statsmodels.api as sm
from statsmodels.genmod.generalized_linear_model import GLMResults
from statsmodels.regression.linear_model import RegressionResults

logger = logging.getLogger(__name__)

Results = Union[RegressionResults, GLMResults]


def evaluate_slm(wrapped: Tuple[pd.DataFrame,
                                pd.Series,
                                pd.Series,
                                pd.DataFrame]) -> pd.DataFrame:
    """
    Fit a simple linear model, evaluate on the testing data and return
    the predictions.
    """
    independents, counts, amounts, testing = wrapped
    with Pool(processes=2) as pool:
        logger.info('Build frequency model: SLM.')
        freq_results = pool.apply_async(build_slm, (counts, independents))

        logger.info('Build severity model: SLM.')
        sev_results = pool.apply_async(build_slm, (amounts, independents))

        freq_predictions = pool.apply_async(freq_results.predict, testing)
        sev_predictions = pool.apply_async(sev_results.predict, testing)

    _log_model_results(freq_results, 'slm_freq')
    _log_model_results(sev_results, 'slm_sev')

    res = pd.concat([freq_predictions, sev_predictions], axis=1)
    res.columns = ['E[N]', 'E[X]']
    return res


def build_slm(wrapped: Tuple[pd.Series, pd.DataFrame]) -> RegressionResults:
    dep, indep = wrapped
    model = sm.OLS(dep, indep)
    return model.fit()


def evaluate_glm(independents: pd.DataFrame,
                 counts: pd.Series,
                 amounts: pd.Series,
                 testing: pd.DataFrame) -> pd.DataFrame:
    """
    Fit a statsmodel GLM using poisson for the frequency and gamma for
    severity.
    """
    logger.info('Build frequency model: GLM.')
    freq_results = build_glm_freq(counts, independents)
    freq_predictions = freq_results.predict(testing)
    _log_model_results(freq_results, 'glm_freq')

    logger.info('Build severity model: GLM.')
    sev_results = build_glm_freq(amounts, independents)
    sev_predictions = sev_results.predict(testing)
    _log_model_results(sev_results, 'glm_sev')

    res = pd.concat([freq_predictions, sev_predictions], axis=1)
    res.columns = ['E[N]', 'E[X]']
    return res


def build_glm_freq(wrapped: Tuple[pd.Series, pd.DataFrame]) -> GLMResults:
    dep, indep = wrapped
    family = sm.families.Poisson(sm.families.links.log)
    model = sm.GLM(dep, indep, family=family)
    return model.fit()


def build_glm_sev(wrapped: Tuple[pd.Series, pd.DataFrame]) -> GLMResults:
    dep, indep = wrapped
    family = sm.families.Gamma(sm.families.links.identity)
    model = sm.GLM(dep, indep, family=family)
    return model.fit()


def _log_model_results(res: Results, name: str) -> None:
    """
    Store the results of a model fitting in a log file.
    """
    logger.info(f'Logging results of {name} model.')
    with open(f'{name}.log', 'w') as f:
        f.write(res.summary().as_text())
