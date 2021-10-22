import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import special, stats
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.stats.proportion import multinomial_proportions_confint

from .utils import filter_dataframe, get_rc_table, get_dummies


def get_basic_distribution_characteristics(x):
    """Log mean, median and interquartile range"""
    logging.info(f"Min (max): {np.min(x)} ({np.max(x)})")
    logging.info(f"Mean: {np.mean(x)}")
    logging.info(f"Median: {np.median(x)}")
    logging.info(
        f"Interquartile range [25-75%]: {' - '.join(stats.mstats.mquantiles(x, [0.25, 0.75]).astype('str'))}"
    )


def normality_test(x):
    """Normality test using the Shapiro Wilks test"""
    logging.info(stats.shapiro(x))


def get_goodman_interval(df, col, alpha=0.05, predictor=None):
    """Compute confidence intervals for a multinomial distribution."""
    rc = get_rc_table(df, col, predictor)
    logging.info(f"Total samples: {rc.sum().sum()}")
    for idx, row in rc.iterrows():
        confints = multinomial_proportions_confint(
            row, alpha=alpha, method="goodman"
        ).squeeze()
        n = row.sort_index()
        logging.info(f"--- {idx} samples: {n.sum()} ---")
        confints = multinomial_proportions_confint(
            row, alpha=alpha, method="goodman"
        ).squeeze()
        for i in range(n.shape[0]):
            confint = confints[i]
            logging.info(f"Confidence interval for efficiency = {df.index[i]}")
            logging.info(
                f"{n[i]/n.sum() * 100:.1f}%\
 (n = {n[i]},\
 95% C.I.: {confint[0] * 100:.1f}% - {confint[1] * 100:.1f}%)\n"
            )


def get_posterior_distributions(df, col="Effectiviteit", predictor=None, plot=True):
    """Compute posterior distributions for a multinomial distribution."""
    rc = get_rc_table(df, col, predictor)
    logging.info(f"Total samples: {rc.sum().sum()}")

    if plot:
        f, axarr = plt.subplots(1, rc.shape[1], figsize=(16, 4))
        theta = np.linspace(0, 1, 1001)
        if rc.shape[1] == 2:
            axarr[0].set_title("response: 0%")
            axarr[1].set_title("response: 50-100%")
        elif rc.shape[1] == 3:
            axarr[0].set_title("response: 0%")
            axarr[1].set_title("response: 50%")
            axarr[2].set_title("response: 100%")
        for k in range(rc.shape[1]):
            axarr[k].set_xlabel("percentage")
            axarr[k].set_xlim(0, 100)

    for idx, row in rc.iterrows():
        n = row.sort_index()
        logging.info(f"--- {idx} samples: {n.sum()} ---")
        alpha = np.ones(n.shape[0])  # uninformative dirichlet prior
        alpha_updated = n + alpha
        alpha_total = alpha_updated.sum()
        for i in range(n.shape[0]):
            posterior = stats.beta(a=alpha_updated[i], b=alpha_total - alpha_updated[i])
            mean = posterior.mean()
            cred_i = posterior.interval(0.95) * 100
            logging.info(f"Posterior for efficiency = {i}")
            logging.info(
                f"{n[i]/n.sum() * 100:.1f}%\
 (n = {n[i]},\
 95% Cred. I.: {cred_i[0] * 100:.1f}% - {cred_i[1] * 100:.1f}%)\n"
            )
            if plot:
                pdf = posterior.pdf(theta)
                if (i == rc.shape[1] - 1) & (predictor is not None):
                    label = idx
                else:
                    label = None
                axarr[i].plot(theta * 100, pdf, label=label)
                axarr[i].set_ylim(0, 25)
                axarr[i].set_xlim(0, 100)
        if plot:
            axarr[-1].legend(loc=1)


def logit_ordinal_regression(
    df,
    dependent_variable,
    predictor,
    drop_categories=None,
):
    """Perform ordinal logistic regression.

    Note: currently no functionality for continuous predictors

    Parameters
    ----------
    df : pd.DataFrame
        Data
    dependent_variable : string
        Column containing variable to be predicted
    predictor : list
        list of columns with the predictors
    drop_categories : dictionary, optional
        Dictionary to set the reference value of each predictor, by default None
    """

    logging.info(f"\nOrdinal regression using {predictor}")
    df = filter_dataframe(df, predictor)

    mod_log = OrderedModel(
        df[dependent_variable].astype("int"),
        get_dummies(df[predictor], drop=drop_categories),
        distr="logit",
    )
    res_log = mod_log.fit(method="nm", disp=False, xtol=1e-3, maxiter=int(1e4))
    logging.info(res_log.summary())
    logging.info(f"Log-likelihoood ratio: {res_log.llr:.2f}")
    logging.info(f"LLR p-value: {res_log.llr_pvalue:.2f}")
    return mod_log, res_log


def chi2_test(df, col, predictor) -> None:
    """Perform Pearson's chi2 on a contingency table."""
    logging.info(f"\nChi-squared test for {predictor} and {col}")
    rc = get_rc_table(df, col, predictor)
    chi2, p, dof, expected = stats.chi2_contingency(rc)

    logging.info("\np-value: %.5f" % p)
    logging.info("dof: %i" % dof)
    logging.info("chi2: %.3f" % chi2)


def kendall_tau(df, x, y, variant="b") -> None:
    """Kendall-tau test for ordinal data."""
    df = filter_dataframe(df, y)
    logging.info(stats.kendalltau(df[x], df[y], variant=variant))
