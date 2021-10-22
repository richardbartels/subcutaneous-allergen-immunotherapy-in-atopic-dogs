import logging

import numpy as np
import pandas as pd

def _rename_columns(df):
    """Rename columns"""

    allergies_1 = df.columns[
        [(".1" in c) & (not "Ras" in c) for c in df.columns]
    ].values
    allergies_plus = np.array([s.replace(".1", "") for s in allergies_1])

    for a in allergies_plus:
        df.rename(
            columns={a: "%s_huidtest" % a, "%s.1" % a: "%s_serologie" % a}, inplace=True
        )
    return df


def load_data(filepath) -> pd.DataFrame:
    """Load the main data file"""
    df = pd.read_excel(
        filepath,
        skiprows=[
            1,
        ],
        index_col=None,
        header=[0],
    )
    df = df.rename({"Fabrikant, ASIT": "Therapie"}, axis=1)

    logging.info(
        f"Number of rows without ASIT test {(df['Start ASIT'] == 'NIET').sum()}"
    )
    logging.info(
        f"Efficiency not measured for all patients without ASIT:\
     {df.loc[df['Start ASIT'] == 'NIET', 'Effectiviteit'].isna().all()}"
    )
    return df


def _clean_age(df):
    """Preprocess the age column in the dataset with ASIT patients."""
    # Assert that patients without a birth date or ASIT start date do not have a registered age at ASIT
    assert (
        df.loc[df["Geboortedatum"].isin(["?", np.nan]), "Leeftijd start"].isna().all()
    )
    assert df.loc[df["Start ASIT"].isin(["?", np.nan]), "Leeftijd start"].isna().all()

    # Set dtype to float
    df["Leeftijd start"] = (
        df["Leeftijd start"].apply(lambda x: str(x).replace(",", ".")).astype("float")
    )

    # Check where age info is present
    df["age_info"] = (~df["Geboortedatum"].isin(["?", np.nan])) & (
        ~df["Start ASIT"].isin(["?", np.nan])
    )
    df["age_info"] = df["age_info"].astype("bool")

    # Impute missing age where information is present
    missing_age = df["age_info"] & df["Leeftijd start"].isna()
    df.loc[missing_age, "Leeftijd start"] = (
        df.loc[missing_age].apply(
            lambda x: (
                pd.to_datetime(x["Start ASIT"], infer_datetime_format=True)
                - pd.to_datetime(x["Geboortedatum"], infer_datetime_format=True)
            )
            / np.timedelta64(1, "Y"),
            axis=1,
        )
    ).astype("float")

    # remove unphysical outliers
    outliers = df["Leeftijd start"] < 0
    logging.info(f"{outliers.sum()} patients with an age below 0, removing.")
    df.loc[outliers, "age_info"] = False
    df.loc[outliers, "Leeftijd start"] = np.nan

    assert ~df.loc[df["age_info"], "Leeftijd start"].isna().any()
    assert df.loc[~df["age_info"], "Leeftijd start"].isna().all()
    logging.info(f"Patients with age information: {df['age_info'].sum()}")

    return df


def _select_asit(df):
    """Select all paitents with AIT treatment."""
    # Assert that patients without ASIT also don't have an efficiency measured.
    assert df.loc[df["Start ASIT"] == "NIET", "Effectiviteit"].isna().all()

    # Remove patients without ASIT
    df = df.loc[df["Start ASIT"] != "NIET"].copy()

    # only keep patients where the efficiency was reported
    df = df.loc[~df["Effectiviteit 03"].isna()]

    assert (
        ~df[["Effectief? 50% ( Ja/nee)", "Volledige remissie (Ja/Nee)"]].isin(
            ["?", np.nan]
        )
    ).values.all()

    logging.info(f"Total number of ASIT patients: {df.shape[0]}")
    logging.info(f"Unique patients: {df['Vetware nummer'].unique().shape[0]}")

    return df

def _get_agegroup(x):
    if x is np.nan:
        return np.nan
    elif x < 4:
        return 0
    elif x <= 8:
        return 1
    elif x > 8:
        return 2


def _get_allergies(df, test='huidtest'):

    allergies_dict = {
            "Huisstofmijt": "Mites",
            "Farinaemijt": "Mites",
            "Copramijt": "Mites",
            "Meelmijt": "Mites",
            "Hooimijt": "Mites",
            "Graspollen": "Grasses",
            "Boompollen": "Trees",
            "Kruiden": "Weeds"}
    cols = [f"{k}_{test}" for k in allergies_dict.keys()]


    def _assign_allergies(row):
        allergies = []
        for k, v in allergies_dict.items():
            if row[f'{k}_{test}'] == 1:
                if not v in allergies:
                    allergies.append(v)
            else:
                pass
        if len(allergies) == 0:
            return 'No mite/tree/weed/grass allergies'
        elif not 'Mites' in allergies:
            return "Pollen only"
        elif len(allergies) == 1:
            return "Mites only"
        elif len(allergies) == 2:
            return "Mites and 1 pollen"
        else:
            return "Mites and 2+ pollen"
        # return '_'.join(allergies)
    if test == 'huidtest':
        colname = 'skintest'
    elif test == 'serologie':
        colname = 'serology'
    df[f'{colname}_performed'] = ~df.loc[:,cols].isna().all(axis=1)
    df[colname] = df.apply(_assign_allergies, axis=1)
    df.loc[~df[f'{colname}_performed'], colname] = np.nan
    return df

def _get_number_of_allergens(df):
    mask = ~df["Therapie"].isna()

    def get_cat(x):
        if x == 1:
            return "1"
        elif x == 2:
            return "2"
        elif x <= 3:
            return "3"
        elif x <= 6:
            return "4-6"
        elif x <= 9:
            return "6-9"
        else:
            return ">9"

    df.loc[mask, "number_allergens"] = df.loc[mask, "Therapie"].apply(
        lambda x: len(x.split(","))
    )
    df.loc[mask, "number_allergens_cat"] = df.loc[mask, "number_allergens"].apply(
        get_cat
    )
    return df


def _expand_medicatiegroep(df):
    """Expand medication group to patients with other and no medication.
    
    No medication was not confirmed, so left out of the analysis.
    """
    mask = (
        df[["Medicatie ten tijde van therapie: systemisch_huidtest", "Medicatiegroep"]]
        .isna()
        .all(axis=1)
    )
    mask.sum()

    mask2 = (
        df[["Medicatie ten tijde van therapie: systemisch_huidtest", "Medicatiegroep"]]
        .isna()
        .sum(axis=1)
        == 1
    )

    assert (
        df[["Medicatie ten tijde van therapie: systemisch_huidtest", "Medicatiegroep"]]
        .isna()
        .sum(axis=0)
        .min()
        == mask.sum()
    )

    df['Medicatiegroep_ext'] = df['Medicatiegroep'].values
    df.loc[mask, "Medicatiegroep_ext"] = 0
    df.loc[mask2, "Medicatiegroep_ext"] = 4
    return df

def get_retriever(df):
    """Add column specifying if a dog is a retriever (cross-breed get a nan)"""
    df['retriever'] = (df['Rasgroep'] == 8).astype('int')
    df.loc[df['Rasgroep'].isna(), 'retriever'] = np.nan
    df.loc[df['Rasgroep'] == 'cb', 'retriever'] = np.nan
    return df

def load_preprocess_data(filepath) -> pd.DataFrame:
    """Load and preprocess the main data file"""
    df = load_data(filepath)
    df = _rename_columns(df)
    df = _get_allergies(df, 'huidtest')
    df = _get_allergies(df, 'serologie')
    df = _select_asit(df)
    df = get_retriever(df)
    df = _clean_age(df)
    df["age_cat"] = df["Leeftijd start"].apply(_get_agegroup)
    df = _get_number_of_allergens(df)
    df = _expand_medicatiegroep(df)

    return df
