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
df = pd.read_excel("../oppsummering.xlsx", sheet_name="data_vasket")

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
df.insert(
    0, "analyse_ID", range(1, len(df) + 1)
)  # legg til en ID for hvert svar for å aggregere
# %%
# variabler som inneholder fritekst
df["brevtype_kort"] = df[
    "Tenk på det siste brevet du fikk fra oss. Hva handlet brevet om?"
]
df["brevtype_kort"] = df["brevtype_kort"].apply(
    lambda x: "Annet" if "Annet" in str(x) else x
)  # bytt ut fritekst med kategori
df["hvem_kort"] = df["Hvem fikk du hjelp fra?"]
df["hvem_kort"] = df["hvem_kort"].apply(
    lambda x: "Andre" if "Andre" in str(x) else x
)  # bytt ut fritekst med kategori
# %%
int_cols = ["analyse_ID"] # int

str_cols = [
    "Er det noe mer du ønsker å fortelle oss i forbindelse med dette brevet? Vi ber deg om å ikke skrive personopplysninger. "
]  # fritekst

cat_cols = list(
    set(df.columns) - set(int_cols) - set(str_cols)
)  # Resterende er kategoriske variabler
# %%
# Sett riktig datatype per variabel
df[cat_cols] = df[cat_cols].astype("category")
df[int_cols] = df[int_cols].astype("Int64")
df[str_cols] = df[str_cols].astype("string")
# %%
# skill ut nominelle kategoriske
nom_cols = [
    "Har du nylig mottatt brev fra oss? Vil du svare på en 5 minutters spørreundersøkelse om brevet?",
    "Tenk på det siste brevet du fikk fra oss. Hva handlet brevet om?",
    "Hvor lang tid brukte du på å lese og forstå brevet? ",
    "Tok du kontakt med NAV for å få hjelp til å forstå brevet?",
    "Hvem fikk du hjelp fra?",
    "brevtype_kort",
    "hvem_kort",
]
# %%
# skill ut ordinale kategoriske
ord_cols = [q for q in cat_cols if q not in nom_cols]
# %%
# sett rekkefølge for ordinale variabler
_ = {
    1: "Helt uenig",
    2: "Uenig",
    3: "Ikke enig eller uenig",
    4: "Enig",
    5: "Helt enig",
    np.nan: np.nan,
}
df[ord_cols] = df[ord_cols].replace(_)
ord_sorted = pd.CategoricalDtype(
    categories=["Helt uenig", "Uenig", "Ikke enig eller uenig", "Enig", "Helt enig"],
    ordered=True,
)
df[ord_cols] = df[ord_cols].astype(ord_sorted)
# %%
# bekreft datatypene er riktige
df.dtypes
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
fig = px.histogram(
    df, x=df[ord_cols[0]]
).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(
    df, x=df[ord_cols[1]]
).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(
    df, x=df[ord_cols[2]]
).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(
    df, x=df[ord_cols[3]]
).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(
    df, x=df[ord_cols[4]]
).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(
    df, x=df[ord_cols[5]]
).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(
    df, x=df[ord_cols[6]]
).update_xaxes(categoryorder="total descending")
fig.show()
# %%
fig = px.histogram(
    df, x=df[ord_cols[7]]
).update_xaxes(categoryorder="total descending")
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