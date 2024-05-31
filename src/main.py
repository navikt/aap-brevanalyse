# %%
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import plot_likert
import plot_likert.scales

import statsmodels.api as sm
from statsmodels.stats.nonparametric import (
    rank_compare_2indep,
    rank_compare_2ordinal,
    prob_larger_continuous,
    cohensd2problarger,
)
from scipy import stats


# %%
df = pd.read_excel("../ny_oppsummering.xlsx", sheet_name="data_vasket")

# %%
"""
Utforsk datasettet
Sett riktig type på hver variabel hvis de ikke er riktige

Dette datasettet inneholder disse datatypene per variabel

kontinuerlige: f.eks analyse_ID, en unik ID for å skille mellom svar fra hver respondent, satt til integer
kategoriske: svarene på spørsmål i likert skala fra 1 til 5, og svar om tidsbruk og type brev de har mottatt
* ordinale: svar på 5punkt likert skala fra "helt uenig" til "helt enig" er ordinale
* nominelle: svar på spørsmål som brevtype, hvem de tok kontakt med og tidsbruk er nominelle
strenger: fritekstsvar, bare ett spørsmål inneholder slike svar "Er det noe mer du ønsker å fortelle oss"
blandede kategoriske og strenger: svar om brevtype og hvem fikk du hjelp fra - alle svar som starter med henholdsvis "Annet" eller "Andre"


pandas tror at noen av variablene er int eller float, men de er kategoriske
Variablene må derfor omkodes til riktig type før de analyseres
"""
# %%
df.info()
# %%
df.dtypes  # se på hvilke datatyper pandas tror variablene består av


# %%
def add_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds an identifier to each row in a pandas dataframe. Returns a copy of the modified dataset.

    Parameters:
    ----------
    df: pd.Dataframe, required

    Returns:
    ---------
    data: pd.Dataframe
    """
    data = df.copy()
    data.insert(0, "analyse_ID", range(1, len(df) + 1))
    return data


# %%
def add_short_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add columns with shorthand names for grouping answers when datatypes are mixed categorical data with open ended answers. Returns a copy of the modified dataset.

    Parameters:
    ----------
    df: pd.Dataframe, required

    Returns:
    ---------
    data: pd.Dataframe
    """
    data = df.copy()
    data["brevtype_kort"] = data[
        "Tenk på det siste brevet du fikk fra oss. Hva handlet brevet om?"
    ]
    data["brevtype_kort"] = data["brevtype_kort"].apply(
        lambda x: "Annet" if "Annet" in str(x) else x
    )  # swap open ended answers with a categorical
    data["hvem_kort"] = data["Hvem fikk du hjelp fra?"]
    data["hvem_kort"] = data["hvem_kort"].apply(
        lambda x: "Andre" if "Andre" in str(x) else x
    )  # swap open ended answers with a categorical
    return data


# %%
def label_col_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Label all the types of variables and return them as lists. Returns a copy of the modified dataset.

    Parameters:
    ------------
    df = pd.Dataframe, required
        The dataframe that will be labeled

    Returns:
    ---------
    data = pd.Dataframe
        The dataframe that will be returned
    int_cols: list
        List of variables that are integer
    str_cols: list
        List of variables that contain strings
    cat_cols: list
        List of all variables that are categorical
    nom_cols: list
        List of all variables that are nominal categoricals
    ord_cols: list
        List of all variables that are ordinal categoricals
    open_cols: list
        List of all variables containing open ended answers, both the string type and mixed categorical type
    """
    data = df.copy()
    int_cols = ["analyse_ID"]  # int
    str_cols = [
        "Er det noe mer du ønsker å fortelle oss i forbindelse med dette brevet? Vi ber deg om å ikke skrive personopplysninger. "
    ]  # open ended
    cat_cols = list(
        set(df.columns) - set(int_cols) - set(str_cols)
    )  # Remainders are categorical
    mixed_cols = [
        "Tenk på det siste brevet du fikk fra oss. Hva handlet brevet om?",
        "Hvem fikk du hjelp fra?",
    ]

    # Set datatype for each variable using the lists
    data[cat_cols] = data[cat_cols].astype("category")
    data[int_cols] = data[int_cols].astype("Int64")
    data[str_cols] = data[str_cols].astype("string")

    # nominal categoricals
    nom_cols = [
        "Har du nylig mottatt brev fra oss? Vil du svare på en 5 minutters spørreundersøkelse om brevet?",
        "Tenk på det siste brevet du fikk fra oss. Hva handlet brevet om?",
        "Hvor lang tid brukte du på å lese og forstå brevet? ",
        "Tok du kontakt med NAV for å få hjelp til å forstå brevet?",
        "Hvem fikk du hjelp fra?",
        "brevtype_kort",
        "hvem_kort",
    ]

    # ordinal categoricals
    ord_cols = [q for q in cat_cols if q not in nom_cols]

    # all open ended variables
    open_cols = str_cols + mixed_cols

    return data, int_cols, str_cols, cat_cols, nom_cols, ord_cols, open_cols


# %%
def order_categoricals(
    df: pd.DataFrame, ordering: dict, columns: list, categories_list: list
) -> pd.DataFrame:
    """
    Add ordering to categorical variables using a dict. Returns a copy of the modified dataset.

    Parameters:
    ----------
    df = pd.Dataframe, required
        the dataframe to modify
    ordering = dict, required
        the dictionary containing mapping from original to new values
    columns = list, required
        the list of columns to modify
    categories_list = list, required
        the list of category labels to order the ordinal variables with

    Returns:
    --------
    data: a dataframe with modified ordinal variables
    """
    data = df.copy()
    # sett rekkefølge for ordinale variabler
    _ = {
        1: "Helt uenig",
        2: "Uenig",
        3: "Ikke enig eller uenig",
        4: "Enig",
        5: "Helt enig",
        np.nan: np.nan,
    }
    data[columns] = data[columns].replace(ordering)
    ord_sorted = pd.CategoricalDtype(
        categories=categories_list,
        ordered=True,
    )
    data[columns] = data[columns].astype(ord_sorted)
    return data


# %%
# last funksjoner for prep
df = add_id(df=df)
df = add_short_cols(df=df)
df, int_cols, str_cols, cat_cols, nom_cols, ord_cols, open_cols = label_col_types(df)
ordering = {
    1: "Helt uenig",
    2: "Uenig",
    3: "Ikke enig eller uenig",
    4: "Enig",
    5: "Helt enig",
    np.nan: np.nan,
}
categories = ["Helt uenig", "Uenig", "Ikke enig eller uenig", "Enig", "Helt enig"]
df = order_categoricals(
    df=df, ordering=ordering, columns=ord_cols, categories_list=categories
)
# %%
# bekreft datatypene er riktige
df.dtypes
# %%
# dropp variabler med fritekst
df.drop(columns=open_cols, inplace=True)
# %%
# inspiser hver variabel for å sjekke sortering
df["Brevet får frem hva jeg kan eller må gjøre etter å ha lest det."]
# %%
df["hvem_kort"]
# %%
# median for ordinale kategoriske
np.median(df["Jeg skjønner hvorfor jeg har mottatt dette brevet."].cat.codes)
# %%
np.median(df["Skriftstørrelsen i brevet passer meg."].cat.codes)
# %%
# modal for nominelle kategoriske
stats.mode(df["Hvor lang tid brukte du på å lese og forstå brevet? "].cat.codes)
# %%
stats.mode(df["hvem_kort"].cat.codes)
# %%
"""
Visualisering
"""
df.groupby(["brevtype_kort"]).agg(brevtyper=("brevtype_kort", "count")).sort_values(
    by="brevtyper", ascending=False
)
# %%
"""
Hvor mange har vi og hvor mange svar mangler vi? 
Skill ut svarene på påstandene
"""
df[ord_cols].isna().sum()
# %%
df[ord_cols].count()
# %%
"""
Histogram per ordinal variabel
"""
fig = px.histogram(df, x=df[ord_cols[0]]).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(df, x=df[ord_cols[1]]).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(df, x=df[ord_cols[2]]).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(df, x=df[ord_cols[3]]).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(df, x=df[ord_cols[4]]).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(df, x=df[ord_cols[5]]).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(df, x=df[ord_cols[6]]).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(df, x=df[ord_cols[7]]).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(
    df, x=df["Hvor lang tid brukte du på å lese og forstå brevet? "]
).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(
    df, x=df["Tok du kontakt med NAV for å få hjelp til å forstå brevet?"]
).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(df, x=df["hvem_kort"]).update_xaxes(categoryorder="total descending")
fig.show()
# %%
# %%
"""
Likert grafer
Disse visualiserer fordelingen av svarene per påstand fra "Helt uenig" til "Helt enig" med
** prosentandel blant svarene
** antall svar
"""

scales = ["Helt uenig", "Uenig", "Ikke enig eller uenig", "Enig", "Helt enig"]
# %%
# Alle brev med alle ordinale variabler
ax = plot_likert.plot_likert(
    df=df[ord_cols].dropna().astype(str),
    plot_scale=scales,
    plot_percentage=True,
    figsize=(14, 4),
)
for bars, color in zip(ax.containers[1:], ["white"] + ["black"] * 2 + ["white"] * 2):
    ax.bar_label(bars, label_type="center", fmt="%.1f %%", color=color)

ax.set_title(("Fordeling svar alle brevtyper"), fontsize=16)
plt.tight_layout()
plt.show()
# %%
# Uttrekk for brevtypene innvilget og avslag, med alle ordinale variabler
innvilget = df[df["brevtype_kort"] == "NAV har innvilget søknaden din om AAP"]
avslag = df[df["brevtype_kort"] == "NAV har avslått søknaden din om AAP"]
fler_opplysninger = df[df["brevtype_kort"] == "Du må sende oss flere opplysninger"]
annet = df[df["brevtype_kort"] == "Annet"]
forlenget = df[df["brevtype_kort"] == "NAV har forlenget perioden din med AAP"]

# %%
# Innvilget med alle ordinale variabler
ax = plot_likert.plot_likert(
    df=innvilget[ord_cols].dropna().astype(str),
    plot_scale=scales,
    plot_percentage=True,
    figsize=(14, 4),
)
for bars, color in zip(ax.containers[1:], ["white"] + ["black"] * 2 + ["white"] * 2):
    ax.bar_label(bars, label_type="center", fmt="%.1f %%", color=color)

ax.set_title((df["brevtype_kort"].unique()[0]), fontsize=16)
plt.tight_layout()
plt.show()
# %%
# antall svar per brevtype innvilget
_ = pd.pivot_table(
    pd.melt(innvilget[ord_cols]),
    index="value",
    columns="variable",
    aggfunc="size",
    fill_value=0,
    observed=False,
)
az = plot_likert.plot_counts(counts=_.transpose(), scale=scales, bar_labels=True)
az.set_title(("Antall svar brevtype innvilget"), fontsize=16)
# %%
# Avslag med alle ordinale variabler
ax = plot_likert.plot_likert(
    df=avslag[ord_cols].dropna().astype(str),
    plot_scale=scales,
    plot_percentage=True,
    figsize=(14, 4),
)
for bars, color in zip(ax.containers[1:], ["white"] + ["black"] * 2 + ["white"] * 2):
    ax.bar_label(bars, label_type="center", fmt="%.1f %%", color=color)

ax.set_title((df["brevtype_kort"].unique()[1]), fontsize=16)
plt.tight_layout()
plt.show()
# %%
# Flere opplysninger
ax = plot_likert.plot_likert(
    df=fler_opplysninger[ord_cols].dropna().astype(str),
    plot_scale=scales,
    plot_percentage=True,
    figsize=(14, 4),
)
for bars, color in zip(ax.containers[1:], ["white"] + ["black"] * 2 + ["white"] * 2):
    ax.bar_label(bars, label_type="center", fmt="%.1f %%", color=color)

ax.set_title((df["brevtype_kort"].unique()[2]), fontsize=16)
plt.tight_layout()
plt.show()
# %%
# Forlenget AAP
ax = plot_likert.plot_likert(
    df=forlenget[ord_cols].dropna().astype(str),
    plot_scale=scales,
    plot_percentage=True,
    figsize=(14, 4),
)
for bars, color in zip(ax.containers[1:], ["white"] + ["black"] * 2 + ["white"] * 2):
    ax.bar_label(bars, label_type="center", fmt="%.1f %%", color=color)

ax.set_title((df["brevtype_kort"].unique()[4]), fontsize=16)
plt.tight_layout()
plt.show()

# %%
# Annet
ax = plot_likert.plot_likert(
    df=annet[ord_cols].dropna().astype(str),
    plot_scale=scales,
    plot_percentage=True,
    bar_labels=True,
    figsize=(14, 4),
)
for bars, color in zip(ax.containers[1:], ["white"] + ["black"] * 2 + ["white"] * 2):
    ax.bar_label(bars, label_type="center", fmt="%.1f %%", color=color)

ax.set_title((df["brevtype_kort"].unique()[3]), fontsize=16)
plt.tight_layout()
plt.show()
