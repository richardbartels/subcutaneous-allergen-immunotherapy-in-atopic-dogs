"""Some utility functions."""
import logging

import numpy as np
import pandas as pd


def get_rc_table(df, col, stratify_by) -> pd.DataFrame:
    """Create a contingency table."""
    if stratify_by is None:
        rc = pd.crosstab(index=np.ones(df.shape[0]), columns=df[col])
    else:
        df = filter_dataframe(df, stratify_by)
        rc = pd.crosstab(index=df[stratify_by], columns=df[col])
    return rc


def filter_dataframe(df, filter_by) -> pd.DataFrame:
    """Drop nans

    Parameters
    ----------
    df : pd.DataFrame
        Data
    filter_by : str or list
        Columns to filter
    """
    if isinstance(filter_by, str):
        df_out = df.dropna(subset=[filter_by]).copy()
    else:
        df_out = df.dropna(subset=filter_by).copy()
    logging.info(f"Patients analyzed: {df_out.shape[0]}")
    return df_out

def get_dummies(df, drop=None):
    """One-hot encode columns for regression analysis.

    One hot encode all columns in the dataframe. For each variable
    one of the outcome columns is dropped since it is fully specified by the others.
    """
    dfs = []
    for col in df.columns:
        temp = pd.get_dummies(df[col])

        cols_out = temp.sum(axis=0).sort_values(ascending=True).index
        if drop is None:
            # drop value with most counts (set this one as reference column)
            cols_out = cols_out[:-1]  # drop last
        else:
            cols_out = np.array([x for x in cols_out if x != drop[col]])
        temp = temp.loc[:, cols_out]
        temp = pd.DataFrame({f"{col}: {c}": temp[c] for c in cols_out})
        dfs.append(temp)
    return pd.concat(dfs, axis=1, ignore_index=False)
