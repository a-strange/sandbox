import pandas as pd
import statsmodels.api as sm


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

    sev_model = sm.OLS(amounts, independents)
    sev_results = sev_model.fit()
    sev_predictions = sev_results.predict(testing)

    print(freq_predictions.head(), sev_predictions.head())
