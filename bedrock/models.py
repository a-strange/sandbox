import logging
from multiprocessing import Pool
from typing import Union

import pandas as pd
import statsmodels.api as sm
from statsmodels.genmod.generalized_linear_model import GLMResults
from statsmodels.regression.linear_model import RegressionResults
from sklearn.ensemble import RandomForestRegressor

logger = logging.getLogger(__name__)

Results = Union[RegressionResults, GLMResults]


def evaluate_slm(independents: pd.DataFrame,
                 counts: pd.Series,
                 amounts: pd.Series,
                 testing: pd.DataFrame) -> pd.DataFrame:
    """
    Fit a simple linear model, evaluate on the testing data and return
    the predictions.
    """
    pool = Pool(processes=2)

    logger.info('Build frequency model: SLM.')
    freq_results = pool.apply_async(build_slm, (counts, independents))

    logger.info('Build severity model: SLM.')
    sev_results = pool.apply_async(build_slm, (amounts, independents))

    freq_results = freq_results.get()
    sev_results = sev_results.get()

    freq_predictions = pool.apply_async(freq_results.predict, [testing])
    sev_predictions = pool.apply_async(sev_results.predict, [testing])

    pool.close()
    pool.join()

    _log_model_results(freq_results, 'slm_freq')
    _log_model_results(sev_results, 'slm_sev')

    res = pd.concat([freq_predictions.get(), sev_predictions.get()], axis=1)
    res.columns = ['E[N]', 'E[X]']
    return res


def build_slm(dep: pd.Series, indep: pd.DataFrame) -> RegressionResults:
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
    pool = Pool(processes=2)

    logger.info('Build frequency model: GLM.')
    freq_results = pool.apply_async(build_glm_freq, (counts, independents))

    logger.info('Build severity model: GLM.')
    sev_results = pool.apply_async(build_glm_sev, (amounts, independents))

    freq_results = freq_results.get()
    sev_results = sev_results.get()

    freq_predictions = pool.apply_async(freq_results.predict, [testing])
    sev_predictions = pool.apply_async(sev_results.predict, [testing])

    pool.close()
    pool.join()

    _log_model_results(freq_results, 'glm_freq')
    _log_model_results(sev_results, 'glm_sev')

    res = pd.concat([freq_predictions.get(), sev_predictions.get()], axis=1)
    res.columns = ['E[N]', 'E[X]']
    return res


def build_glm_freq(dep: pd.Series, indep: pd.DataFrame) -> GLMResults:
    family = sm.families.Poisson(sm.families.links.log)
    model = sm.GLM(dep, indep, family=family)
    return model.fit()


def build_glm_sev(dep: pd.Series, indep: pd.DataFrame) -> GLMResults:
    family = sm.families.Gamma(sm.families.links.identity)
    model = sm.GLM(dep, indep, family=family)
    return model.fit()


def evaluate_mlm(independents: pd.DataFrame,
                 counts: pd.Series,
                 amounts: pd.Series,
                 testing: pd.DataFrame) -> pd.DataFrame:

    logger.info('Build frequency model: MLM.')
    freq_results = build_mlm(counts, independents)
    freq_predictions = freq_results.predict(testing)

    logger.info('Build severity model: MLM.')
    sev_results = build_mlm(amounts, independents)
    sev_predictions = sev_results.predict(testing)

    res = pd.np.column_stack((freq_predictions,
                              sev_predictions,
                              testing.pol_id))
    res = pd.DataFrame(res, coluns=['pol_id', 'E[N]', 'E[X]'])
    res.set_index('pol_id')
    return res


def build_mlm(dep: pd.Series, indep: pd.DataFrame) -> RandomForestRegressor:
    rf = RandomForestRegressor(n_estimators=1000, random_state=42, n_jobs=-1)
    rf.fit(indep, dep)
    return rf


def _log_model_results(res: Results, name: str) -> None:
    """
    Store the results of a model fitting in a log file.
    """
    logger.info(f'Logging results of {name} model.')
    with open(f'{name}.log', 'w') as f:
        f.write(res.summary().as_text())
