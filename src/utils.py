import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import textwrap
import data_clean


# TODO: 

#%%


#####
# Functions for data wrangling
#####
def finn_kolonner_med_fem_pkt_likert(df_inn: pd.DataFrame) -> pd.Index:
    """
    Identifies columns in the DataFrame that contain a 5-point Likert scale.

    Parameters:
    df_inn (pd.DataFrame): The input DataFrame to be checked.

    Returns:
    pd.Index: Index of columns that contain the 5-point Likert scale.
    """
    er_likert = (df_inn.apply(set) == set(['Enig', 'Helt enig', 'Helt uenig', 'Uenig', 'Verken eller', np.nan]))
    return er_likert.index[er_likert]


def finn_gjelder_brevtype_per_kolonne(
    df_inn: pd.DataFrame,
    kolonne_navn: str,
    brevtype_spørsmål: str = 'Tenk på det siste brevet du fikk fra oss om AAP. Hva handlet brevet om?',
    ) -> str:
    """
    This function determines the applicable letter type(s) for a given column in a DataFrame.

    Parameters:
    df_inn (pd.DataFrame): The input DataFrame containing the data.
    kolonne_navn (str): The name of the column to analyze.
    brevtype_spørsmål (str, optional): The question related to the letter type. Defaults to 'Tenk på det siste brevet du fikk fra oss om AAP. Hva handlet brevet om?'.

    Returns:
    str: A string describing the applicable letter type(s). Possible return values are:
        - A single letter type if only one is applicable.
        - Two letter types separated by "og" if exactly two are applicable.
        - "Alle brevtyper" if exactly four letter types are applicable.
        - "Alle brevtyper, inkludert 'ingen av disse'" if more than four letter types are applicable.
    """
    count_nan = lambda x: (~x.isna()).sum() # Teller alle ikke-nan verdier i en pd.DataFrame-kolonne
    df_brevtype_count = df_inn.groupby(brevtype_spørsmål, observed = True)[kolonne_navn].agg(count_nan)
    gjelder_brevtype_liste = df_brevtype_count[df_brevtype_count != 0].index.to_list()
    if len(gjelder_brevtype_liste) == 1:
        return gjelder_brevtype_liste[0]
    elif len(gjelder_brevtype_liste) == 2:
        return f"{gjelder_brevtype_liste[0]} og {gjelder_brevtype_liste[1]}"
    elif len(gjelder_brevtype_liste) == 4:
        return "Alle brevtyper"
    elif len(gjelder_brevtype_liste) > 4:
        return 'Alle brevtyper, inkludert "ingen av disse"'


def finn_gjelder_brevtype_som_Serie(df_inn: pd.DataFrame) -> pd.Series:
    """
    This function processes a DataFrame to determine relevant letter types for each column.

    Args:
        df_inn (pd.DataFrame): The input DataFrame containing data to be analyzed.

    Returns:
        pd.Series: A pd.Series containing the relevant letter types for each column in the input DataFrame.

    Functionality:
        - Iterates over each column in the input DataFrame.
        - Applies the `finn_gjelder_brevtype_per_kolonne` function to each column to determine the relevant letter type.
        - Constructs a new DataFrame with the results, where the index corresponds to the original column names and the values are the relevant letter types.
    """
    gjelder_brevtype_liste = [finn_gjelder_brevtype_per_kolonne(df_inn = df_inn, kolonne_navn=k) for k in df_inn.columns]
    ser_ut = pd.Series(gjelder_brevtype_liste, index = df_inn.columns, dtype = str)
    return ser_ut

#%%


#%%
####
# Functions for plotting
####

def plot_likert(spm: str, data_oppsummert: pd.DataFrame, kodebok:pd.DataFrame, gruppering_etter_kolonne:str ="Tenk på det siste brevet du fikk fra oss om AAP. Hva handlet brevet om?", plott_prosent: bool = True, showlegend_bool: bool = True ):
    
    """
    Plots a Likert scale bar chart based on the given data.
    
    Parameters:
    - spm (str): The question identifier.
    - data_oppsummert (pd.DataFrame): The summarized data containing responses.
    - kodebok (pd.DataFrame): The codebook containing question types and other metadata.
    - gruppering_etter_kolonne (str, optional): The column name to group by. Default is "Tenk på det siste brevet du fikk fra oss om AAP. Hva handlet brevet om?".
    - plott_prosent (bool, optional): Whether to plot percentages. Default is True.
    - showlegend_bool (bool, optional): Whether to show the legend. Default is True.
    
    Returns:
    - list: A list of plotly.graph_objects.Bar traces for the Likert scale plot.
    """
    
        
    #Initalisere input
    if kodebok.loc[spm, "SpørsmålType"] == "Likert":
        kategorier= ['Helt uenig', 'Uenig', 'Verken eller', 'Enig', 'Helt enig']

        antall_negative_kategorier = 2
        colors = [
                "#de425b",  # Strongly Disagree bars
                "#ea936d",  # Disagree bar
                "#fbdbb1",  # "Neutral" bars
                "#b2b264",  # "Agree" bars
                "#488f31"  # "Strongly Agree" bars
                ]
        #Fiks format på likert
        kategorier = (pd.Series(kategorier)
                            .astype(
                                CategoricalDtype(kategorier, ordered = True)
                            )
                        )
    elif kodebok.loc[spm, "SpørsmålType"] == "Ja/Nei":
        kategorier= ["Nei", "Ja"]

        antall_negative_kategorier = 1
        colors = [
                "#ea936d",  # Nei bars
                "#b2b264"  # Ja bars
                ]
        #Fiks format på likert
        kategorier = (pd.Series(kategorier)
                            .astype(
                                CategoricalDtype(kategorier, ordered = True)
                            )
                        )
    elif kodebok.loc[spm, "SpørsmålType"] == "Likert Tidsbruk":
        kategorier= ['5 minutter', '15 minutter', '30 minutter', '1 time', 'Mer enn 1 time']

        antall_negative_kategorier = 2
        colors = [
            "#5ad45a",
            "#00b7c7",
            "#1a53ff",
            "#7c1158",
            "#b30000"
            ] 

        #Fiks format på likert
        kategorier = (pd.Series(kategorier)
                            .astype(
                                CategoricalDtype(kategorier, ordered = True)
                            )
                        )
    

    
    negative_kategorier = kategorier[:antall_negative_kategorier][::-1] #Snu rekkefølge på negative kategorier
    positive_kategorier = kategorier[antall_negative_kategorier:]

    
    # initalisere for plotting
    ## Filtrere data:
    df_plot = data_oppsummert.loc[data_oppsummert["Spørsmål"] == spm,:]
    ## Initialisere liste for traces og rangering av legend
    legendrank_count = antall_negative_kategorier
    traces = []

    #Start plotting av et spørsmål for brevkategorier
    for kat in negative_kategorier:
        legendrank_count -= 1
        traces.append(
            go.Bar(
                x=-df_plot[kat].values/df_plot["Totalt svar"]*100,
                y=df_plot[gruppering_etter_kolonne],
                orientation='h',
                name=kat,
                customdata=df_plot[kat].values/df_plot["Totalt svar"]*100,
                legendgroup=kat,
                legendrank = legendrank_count,
                hovertemplate = "%{customdata:.3s} %",
                marker=dict(color=colors[legendrank_count]),
                showlegend=showlegend_bool
                )
            )


    
    legendrank_count = antall_negative_kategorier - 1
    for kat in positive_kategorier:
        legendrank_count += 1
        traces.append(
            go.Bar(
                x=df_plot[kat].values/df_plot["Totalt svar"]*100,
                y=df_plot[gruppering_etter_kolonne],
                orientation='h',
                name=kat,
                #customdata=df_plot[kat].values/df_plot["Totalt svar"]*100,
                legendgroup=kat,
                legendrank = legendrank_count,
                marker=dict(color=colors[legendrank_count]),
                hovertemplate = "%{x:.3s} %",
                showlegend=showlegend_bool
                )
            )
    

    return traces