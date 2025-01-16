import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np
import datetime as dt


def df_oppsummering_per_spm(spm: str,
                    data: pd.DataFrame, 
                    kodebok: pd.DataFrame, 
                    gruppering_etter_kolonne = "Tenk på det siste brevet du fikk fra oss om AAP. Hva handlet brevet om?") -> pd.DataFrame:
    """
    Summarizes a DataFrame based on a specific question and grouping column.
    
    Parameters:
    - spm (str): The question to summarize.
    - data (pd.DataFrame): The DataFrame containing the data to summarize.
    - kodebok (pd.DataFrame): The DataFrame containing metadata about the questions.
    - gruppering_etter_kolonne (str, optional): The column to group by. Defaults to "Tenk på det siste brevet du fikk fra oss om AAP. Hva handlet brevet om?".
    
    Returns:
    - pd.DataFrame: A DataFrame containing the summarized data.
    """
    
    def _lag_oppsummeringer(
        spm: str,
        df_inn: pd.DataFrame = data, 
        gruppering_etter_kolonne:str =gruppering_etter_kolonne):
        """
        Oppsummerer data basert på en spesifisert kolonne og spørsmål.
        
        Args:
            spm (str): Spørsmålskolonnen som skal oppsummeres.
            df_inn (pd.DataFrame, optional): Inndata DataFrame. Default er 'data'.
            gruppering_etter_kolonne (str, optional): Kolonnenavn for gruppering. Default er 'gruppering_etter_kolonne'.
            
        
        Returns:
            tuple or pd.DataFrame: Returnerer en tuple med oppsummerings-DataFrame og deskriptiv statistikk DataFrame hvis `lagDeskriptivStatistikk` er True og spørsmålet er av typen Likert. Ellers returneres kun oppsummerings-DataFrame.
        """


        df_oppsummere = (
            df_inn[[gruppering_etter_kolonne, spm]]
            .astype({gruppering_etter_kolonne:str})
            .pivot_table(
                index=gruppering_etter_kolonne,
                columns=spm,
                aggfunc = "value_counts",
                observed = False,
                dropna = False
            )
            .reset_index()
        )

        #Legg inn kolonne med total for alle kategorier, ekskl. Nans
        df_oppsummere["Totalt svar"] = df_oppsummere.iloc[:,2:].sum(axis = 1)
        
        bool_lag_deskriptiv = kodebok.loc[spm, ["SpørsmålType"]].isin(["Likert", "Likert Tidsbruk"]).any()
        if bool_lag_deskriptiv:
            rekoding = {'5 minutter': 5, 'Mer enn 1 time': 90, '15 minutter':15, '1 time':60, '30 minutter':30} if (spm == "Cirka hvor lang tid tok det å forstå brevet?") else {'Helt enig': 5, 'Enig':4,'Verken eller': 3,'Uenig': 2, 'Helt uenig':1}
            # Legg til kolonner med `pd.describe()`-data:
            df_describe = (
                df_inn[[gruppering_etter_kolonne, spm]]
                    .astype(str)
                    .replace(
                        {spm:rekoding}
                    )
                    .astype({spm:"float64"})
                    .groupby(gruppering_etter_kolonne)
                    .describe()
                    .reset_index()
            )
            #Slå ned kolonnennavn fra mulitindex:
            df_describe.columns = [df_describe.columns.get_level_values(0)[0]] + df_describe.columns.get_level_values(1).to_list()[1:]
            return df_oppsummere, df_describe
        else:
            return df_oppsummere
    def _lag_totalrad(
        total_navn: str, df_oppsummere, df_describe,
        df_inn: pd.DataFrame = data, 
        gruppering_etter_kolonne:str =gruppering_etter_kolonne):
        
        """
        Adds a total row to the summary DataFrame and optionally updates the describe DataFrame.
        
        Parameters:
        - total_navn (str): The name for the total row.
        - df_oppsummere (pd.DataFrame): The DataFrame to which the total row will be added.
        - df_describe (pd.DataFrame or None): The DataFrame containing descriptive statistics to be updated.
        - df_in (pd.DataFrame, optional): The input DataFrame. Defaults to `data`.
        - gruppering_etter_kolonne (str, optional): The column name used for grouping. Defaults to `gruppering_etter_kolonne`.
        
        Returns:
        - pd.DataFrame: Updated df_oppsummere with the total row added.
        - tuple: If df_describe is not None, returns a tuple of (df_oppsummere, df_describe) with the total row added to both.
        """
        
        
        total_liste = [total_navn] + df_oppsummere.iloc[:,1:].sum(axis = 0).to_list()
        total_rad_oppsummert = pd.DataFrame(total_liste, index = df_oppsummere.columns).T
        df_oppsummere = pd.concat(
                        [
                            df_oppsummere,
                            total_rad_oppsummert
                        ])
        if df_describe is not None:
            rekoding = {
                '5 minutter': 5, 'Mer enn 1 time': 90, '15 minutter':15, '1 time':60, '30 minutter':30
                } if (spm == "Cirka hvor lang tid tok det å forstå brevet?") else {
                    'Helt enig': 5,    'Enig':4,'Verken eller': 3,'Uenig': 2, 'Helt uenig':1
                    }
            describe_total_rad = (
                df_inn[[spm]]
                    .astype(str)
                    .replace(
                    {spm:rekoding}
                    )
                    .astype({spm:"float64"})
                    .describe()
                    .T
                    .reset_index()
                )
            describe_total_rad.columns = df_describe.columns

            df_describe = pd.concat(
                [
                    df_describe,
                    describe_total_rad
                ])
            df_describe.iloc[-1,0] = df_oppsummere.iloc[-1, 0]
            return df_oppsummere, df_describe
        else:
            return df_oppsummere
        #####
        
    
    if kodebok.loc[spm,"SpørsmålType"] == "Likert":
        df_oppsummere_uten_total_rad, df_describe_uten_total_rad = _lag_oppsummeringer(spm)
        
        if len(kodebok.loc[spm, "GjelderBrevtype"]) >1:
            if gruppering_etter_kolonne == 'Tenk på det siste brevet du fikk fra oss om AAP. Hva handlet brevet om?':
                #   Dersom sortering er på *brev* med svar fra *mer enn en brevkategori*
                df_oppsummere, df_describe = _lag_totalrad("<i>Total, alle brevtyper</i>", df_oppsummere_uten_total_rad, df_describe_uten_total_rad)
            else:
                df_oppsummere, df_describe = _lag_totalrad("<i>Totalt</i>", df_oppsummere_uten_total_rad, df_describe_uten_total_rad)
        else:
            df_oppsummere, df_describe = df_oppsummere_uten_total_rad, df_describe_uten_total_rad

        df_oppsummere["Spørsmål"] = spm
        df_oppsummere["SpørsmålNummer"] = kodebok.loc[spm, "SpørsmålNummer"]

        #df som skal returneres:
        df_oppsummert = df_oppsummere.merge(df_describe, on = gruppering_etter_kolonne)
    
    elif spm == "Cirka hvor lang tid tok det å forstå brevet?":
        df_oppsummere_uten_total_rad, df_describe_uten_total_rad = _lag_oppsummeringer(spm)

        if gruppering_etter_kolonne == 'Tenk på det siste brevet du fikk fra oss om AAP. Hva handlet brevet om?':
            # Dersom sortering er på *brev* med svar fra *mer enn en brevkategori*
            df_oppsummere, df_describe = _lag_totalrad("<i>Total, alle brevtyper</i>", df_oppsummere_uten_total_rad, df_describe_uten_total_rad)
        else:
            df_oppsummere, df_describe = _lag_totalrad("<i>Totalt</i>", df_oppsummere_uten_total_rad, df_describe_uten_total_rad)

        df_oppsummere["Spørsmål"] = spm
        df_oppsummere["SpørsmålNummer"] = kodebok.loc[spm, "SpørsmålNummer"]
        
        # df som skal returneres
        df_oppsummert = df_oppsummere.merge(df_describe, on = gruppering_etter_kolonne)

    elif (kodebok.loc[spm,"SpørsmålType"] != "Likert") & (kodebok.loc[spm,"SpørsmålType"] != "Likert Tidsbruk"):
        df_oppsummere_uten_totalrad = _lag_oppsummeringer(spm)
        
        if len(kodebok.loc[spm, "GjelderBrevtype"]) >1:
            if gruppering_etter_kolonne == 'Tenk på det siste brevet du fikk fra oss om AAP. Hva handlet brevet om?':
                # Dersom sortering er på *brev* med svar fra *mer enn en brevkategori*
                df_oppsummert = _lag_totalrad("<i>Total, alle brevtyper</i>", df_oppsummere_uten_totalrad, None)
            else:
                df_oppsummert = _lag_totalrad("<i>Totalt</i>", df_oppsummere_uten_total_rad, None)
        df_oppsummert["Spørsmål"] = spm
        df_oppsummert["SpørsmålNummer"] = kodebok.loc[spm, "SpørsmålNummer"]
    # Nytt navm på kolonne med "mangler svar"

    idx_nan = df_oppsummert.columns.get_loc(np.nan)
    kolonnenavn = df_oppsummert.columns.to_list()
    kolonnenavn[idx_nan] = "Mangler svar"
    df_oppsummert.columns = kolonnenavn
    return df_oppsummert.infer_objects()


def func_oppsummer_data(data: pd.DataFrame, kodebok: pd.DataFrame, gruppering_etter_kolonne: str = "Tenk på det siste brevet du fikk fra oss om AAP. Hva handlet brevet om?"):
    """
    Summarizes data based on the type of questions specified in the kodebok.
    
    Parameters:
    - data (pd.DataFrame): The main DataFrame containing the survey data.
    - kodebok (pd.DataFrame): A DataFrame containing metadata about the survey questions, including their types.
    - gruppering_etter_kolonne (str, optional): The column name to group the data by. Default is "Tenk på det siste brevet du fikk fra oss om AAP. Hva handlet brevet om?".
    
    Returns:
    - tuple: A tuple containing three DataFrames:
        - df_likert: Summary of Likert scale questions.
        - df_JaNei: Summary of Yes/No questions.
        - df_Tidsbruk: Summary of Likert scale time usage questions.
    """
    
    
    likert_spørsmål = kodebok.loc[kodebok["SpørsmålType"] == "Likert", "Variabel"].to_list()
    df_likert = []
    
    for spm in likert_spørsmål:
        df_likert.append(df_oppsummering_per_spm(spm, kodebok = kodebok, data = data))
    df_likert = pd.concat(df_likert)

    JaNei_spørsmål = kodebok.loc[kodebok["SpørsmålType"] == "Ja/Nei", "Variabel"].to_list()
    df_JaNei = []
    for spm in JaNei_spørsmål:
        df_JaNei.append(df_oppsummering_per_spm(spm=spm, kodebok = kodebok, data = data))
    df_JaNei = pd.concat(df_JaNei)

    Tidsbruk_spørsmål = kodebok.loc[kodebok["SpørsmålType"] == "Likert Tidsbruk", "Variabel"].to_list()
    df_Tidsbruk = df_oppsummering_per_spm(spm=Tidsbruk_spørsmål[0], kodebok = kodebok, data = data)
    
    
    return df_likert, df_JaNei, df_Tidsbruk