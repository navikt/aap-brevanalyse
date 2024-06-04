#######
#
# 2024.31.25
# 
# Genererer plot som brukes i Dashboard.
#%% 
import pandas as pd
from pandas.api.types import CategoricalDtype
from IPython.display import Markdown as md
from IPython.display import display, HTML
#from tabulate import tabulate

import numpy as np
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

#import missingno as msno
#import matplotlib.pyplot as plt
#import seaborn as sns
import datetime as dt
from plotly.subplots import make_subplots

import pingouin as pg

#%%
df_inn = pd.read_excel("../data/datasett.xlsx")


#%%

#Last inn data
def last_inn_data() -> pd.DataFrame:
    df_ = pd.read_csv("/Users/anderslauvland/DS_AAP/data_Hotjar/Brev_23_24/HJ_brev_data240523.csv",
                     sep=";",
                     #skiprows=1,
                     dtype = {'Har du nylig mottatt brev fra oss? Vil du svare på en 5 minutters spørreundersøkelse om brevet?':'category',
                     #, "Date Submitted": "datetime64"
                     })

    df_dat = df_.drop(columns=['User', 
                        'Country', 
                        'Source URL', 
                        'Device',
                        'Browser', 
                        'OS', 
                        'Hotjar User ID',
                        "Gi poeng til brevet ved å svare på påstandene (trykk neste).",
                        "Takk for dine svar så langt :). \nVi har noen få avsluttende spørsmål igjen (trykk neste). ",
                        'Tags for: Har du nylig mottatt brev fra oss? Vil du svare på en 5 minutters spørreundersøkelse om brevet?',
                        'Brevet er luftig og lett å finne fram i. ',
                        'Det er lett å få oversikt over innholdet i brevet.',
       'Det er lett å lese setningene i brevet.',
       'Tags for: Tenk på det siste brevet du fikk fra oss. Hva handlet brevet om?',
       'Tags for: Gi poeng til brevet ved å svare på påstandene (trykk neste).',
       'Tags for: Jeg skjønner hvorfor jeg har mottatt dette brevet.',
       'Tags for: Brevet får frem hva jeg kan eller må gjøre etter å ha lest det.',
       'Tags for: Det var lett å finne den informasjonen i brevet som er viktigst for meg.',
       'Tags for: Overskriftene i brevet forteller meg hva teksten handler om. ',
       'Tags for: Jeg forstår alle ordene som er brukt i brevet.',
       'Tags for: Brevet henvender seg direkte til meg som person.',
       'Tags for: Brevet inneholder ingen skrivefeil. ',
       'Tags for: Skriftstørrelsen i brevet passer meg.',
       'Tags for: Takk for dine svar så langt :). \nVi har noen få avsluttende spørsmål igjen (trykk neste). ',
       'Tags for: Hvor lang tid brukte du på å lese og forstå brevet? ',
       'Tags for: Tok du kontakt med NAV for å få hjelp til å forstå brevet?',
       'Tags for: Hvem fikk du hjelp fra?',
       'Tags for: Er det noe mer du ønsker å fortelle oss i forbindelse med dette brevet? Vi ber deg om å ikke skrive personopplysninger. ',
       'Tags for: Brevet er luftig og lett å finne fram i. ',
       'Tags for: Det er lett å få oversikt over innholdet i brevet.',
       'Tags for: Det er lett å lese setningene i brevet.',
       'Sentiment for: Er det noe mer du ønsker å fortelle oss i forbindelse med dette brevet? Vi ber deg om å ikke skrive personopplysninger. '])
    df_dat["Date Submitted"] = pd.to_datetime(df_dat["Date Submitted"])
    Annet = "Tenk på det siste brevet du fikk fra oss. Hva handlet brevet om?"
    df = df_dat.copy(deep = True)
    df.loc[(df[Annet].str.rfind("Annet") +1).astype("boolean"), Annet] = "Annet"
    return df

#%% 
def lag_gruppering(df_dat: pd.DataFrame) -> pd.DataFrame:
    

    df_1 = df_dat[["Date Submitted"]].groupby([df_dat["Date Submitted"].dt.year,
                                      df_dat["Date Submitted"].dt.month]
                                     ).count().rename(index={"Date Submitted":"Totalt"})

    df_2 = df_dat.loc[df_dat["Har du nylig mottatt brev fra oss? Vil du svare på en 5 minutters spørreundersøkelse om brevet?"] == "Ja",
                             "Number"].groupby([df_dat["Date Submitted"].dt.year,
                                                df_dat["Date Submitted"].dt.month]
                                               ).count()

    df = pd.concat([df_1, df_2], axis=1)

    df_mnd = df.rename(columns={"Date Submitted":"Totalt", "Number":"Ja"}).copy(deep=True)


    df_mnd.index.set_names(['År', 'Måned'], inplace=True)
    df_mnd.reset_index(inplace=True)
    

    df_mnd['Dato'] = pd.to_datetime(df_mnd.År.astype(str) + '/' + df_mnd.Måned.astype(str) + '/01')



    d_iso = df_dat["Date Submitted"].dt.isocalendar()

    week_date = pd.Series(name = "Week_date", index = d_iso.index)
    for d in d_iso.index:
        week_date[d] = str(pd.Timestamp.fromisocalendar(d_iso.loc[d, "year"], d_iso.loc[d, "week"], 1))
    week_no = d_iso.loc[:, "week"]
    week_date = week_date.astype("datetime64[ns]")

    pd.concat([week_no, week_date], axis=1)


    df_1 = df_dat[["Date Submitted"]].groupby([df_dat["Date Submitted"].dt.year,
                                      week_no, week_date]
                                     ).count().rename(index={"Date Submitted":"Totalt"})

    df_2 = df_dat.loc[df_dat["Har du nylig mottatt brev fra oss? Vil du svare på en 5 minutters spørreundersøkelse om brevet?"] == "Ja",
                             "Number"].groupby([df_dat["Date Submitted"].dt.year,
                                                week_no, week_date]
                                               ).count()

    df = pd.concat([df_1, df_2], axis=1)

    df_uke = df.rename(columns={"Date Submitted":"Totalt", "Number":"Ja"}).copy(deep=True)
    df_uke.index.set_names(['År', 'Uke', 'Dato'],inplace = True)
    df_uke.reset_index(inplace=True)

    return df_mnd



def plot_hj_svar(df_mnd: pd.DataFrame, show: bool, subplots: bool):
    """
    Sammendrag:
    Plotter svarfordeling over tid sammen med total svarfordeling på spørsmålet:
    'Har du nylig mottatt brev fra oss? Vil du svare på en 5 minutters spørreundersøkelse om brevet?'
    
    Args:
        df_mnd (pd.DataFrame): Svarfordeling aggregert på måned
        show (bool): Skal man vise figuren, eller ikke

    Returns:
        go.Figure: plotly.Graph_objects.Figure objekt som er plottet beskrevet i sammendrag.
    """
    if subplots:
        fig = make_subplots(rows=1, cols=2, 
                            shared_yaxes=False, 
                            shared_xaxes=False, 
                            column_widths=[0.7, 0.3],
                            subplot_titles=("Svarfordeling over tid", "Total svarfordeling"))


        fig.add_trace(go.Bar(
            x=df_mnd["Dato"],
            y=df_mnd["Totalt"],
            text = df_mnd["Totalt"],

            name = "Totalt",
            legendgroup = "1",
            marker=dict(color='royalblue'),


            hoverinfo="text",
            xhoverformat="%",
            hovertemplate="%{y} %{_xother}",
            ), 
                      row = 1, col = 1)

        fig.add_trace(go.Bar(
            x=df_mnd["Dato"],
            y=df_mnd["Ja"],
            text = df_mnd["Ja"],
            name="Ja til spørreundersøkelse",
            legendgroup = "2",
            marker=dict(color='firebrick'),

            xhoverformat=None,
            hovertemplate="%{y}",

        ), row = 1, col = 1)    

        fig.add_trace(go.Bar(
            x=["Totalt"],
            y=[df_mnd["Totalt"].sum()],
            name="Totalt",
            legendgroup = "1",
            marker=dict(color='royalblue'),
            showlegend=False,

            xhoverformat=None,
            hovertemplate="%{y}",
            text=[df_mnd["Totalt"].sum()]

        ), row = 1, col = 2)
        fig.add_trace(go.Bar(
            x=["Ja"],
            y=[df_mnd["Ja"].sum()],
            name="Ja til spørreundersøkelse",
            legendgroup = "2",
            showlegend=False,
            marker=dict(color='firebrick'),
            #xperiod="M1",
            #xperiodalignment="middle",
            xhoverformat=None,
            hovertemplate="%{y}",
            text=[df_mnd["Ja"].sum()]

        ),row = 1, col = 2) 

        fig.update_layout(hovermode="closest",
                          barmode = "group")
        fig.update_yaxes(title_text='Antall svar')    
        fig.update_xaxes(title_text='Måned', row=1, col=1)
        fig.update_xaxes(title_text='Totalt/Ja til undersøkelse', row=1, col=2)
    else: 
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_mnd["Dato"],
            y=df_mnd["Totalt"],
            text = df_mnd["Totalt"],
            name = "Totalt",
            marker=dict(color='royalblue'),
            hoverinfo="text",
            xhoverformat="%",
            hovertemplate="%{y} %{_xother}",
            ))

        fig.add_trace(go.Bar(
            x=df_mnd["Dato"],
            y=df_mnd["Ja"],
            text = df_mnd["Ja"],
            name="Ja til spørreundersøkelse",
            marker=dict(color='firebrick'),

            xhoverformat=None,
            hovertemplate="%{y}",

        )) 
    if show:
        fig.show()
        
        
    N = df_mnd["Ja"].sum()
    return fig, N



def gjennomsnittlig_lesetid(df: pd.DataFrame):
    """
    This function creates a bar plot of the average reading time for 
    different types of letters.

    Parameters:
    df (pandas.DataFrame): DataFrame med rådata fra Hotjar.

    Returns: plotly.graph_objs._figure.Figure: En plotly figure som inneholder
            stolpediagrammet.
                Stolpediagrammet viser gjennomsnittlig lesetid for hver type brev. 
            X-aksen representerer de forskjellige typene brev, og y-aksen 
            representerer gjennomsnittlig lesetid i minutter. Gjennomsnittlig 
            lesetid vises også på hver stolpe.
                En horisontal linje er lagt til plottet for å representere den totale
            gjennomsnittlige lesetiden for alle typer brev. Posisjonen til linjen 
            bestemmes av gjennomsnittet av ‘Tidsbruk_skår’. 
            Linjen er grønn og stiplet, og en merknad er lagt til øverst til høyre på
            plottet for å indikere verdien av den totale gjennomsnittlige lesetiden.
                Funksjonen returnerer Figure-objektet. For å vise plottet, kan du bruke 
            'show()'-metode.
            
            float: Gjennomsnittlig lesetid for alle brevgrupper.
            
            pd.DataFrame.style: En DataFrame som viser kodingen av lesetidene i minutter.     
    """
    
    q_tidsbruk = 'Hvor lang tid brukte du på å lese og forstå brevet? '
    q_brevtype = 'Tenk på det siste brevet du fikk fra oss. Hva handlet brevet om?'
    
    dict_tidsbruk_koder = {"Omtrent 5 minutter": 5,
                            "Omtrent 15 minutter": 15,
                            "Omtrent 30 minutter": 30,
                            "Omtrent 1 time":60,
                            "Mer enn 1 time":90}
    df["Tidsbruk_skår"] = np.nan

    index_not_nan = df.loc[~df[q_tidsbruk].isna(), "Tidsbruk_skår"].index
    
    df.loc[~df[q_tidsbruk].isna(), "Tidsbruk_skår"] = pd.Series(
                                                    [dict_tidsbruk_koder[key] for key in df.loc[~df[q_tidsbruk].isna(), q_tidsbruk] ],
                                                    index = index_not_nan
                                                    )


    


    df_plt = df.groupby(q_brevtype)["Tidsbruk_skår"].describe()

    fig = go.Figure()
    fig.add_trace(go.Bar(x = df_plt.index, 
                     y = df_plt["mean"].round(1),
                     text=df_plt["mean"].round(1),
                     texttemplate="%{y} minutter",

                     textposition='auto'))
    dato = str(dt.date.today())
    fig.add_hline(y=df["Tidsbruk_skår"].mean(), line_width=3, line_dash="dash", line_color="green", 
                 annotation_text=f"Gjennomsnitt, alle brevgrupper<br> per. {dato}: {df["Tidsbruk_skår"].mean().round(1)} minutter", 
                 annotation_position="top right",
                 annotation_font_size=12,
                 annotation_font_color="green"
                )
    
    
    # Df med koder: 
    df_kode = (pd.DataFrame.from_dict(dict_tidsbruk_koder, orient = "index", columns = ["Kodet til<br> minutter"])
                           .reset_index()
                           .rename(columns={"index":"Kategorier i<br> spørreskjema"})
                           )
    df_kode.style.hide()
    
    return fig, df["Tidsbruk_skår"].mean(), df_kode.style.hide()



def gjennomsnitts_skår(df: pd.DataFrame) -> dict:
    """
    This function calculates the average score for different indicators in a DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data. It should have columns for each of the indicators.

    Returns:
    dict: A dictionary containing the average score, standard deviation, count, and Cronbach's alpha for the indicators.

    The function first defines a list of indicators. These are the column names in the DataFrame that the function will calculate the average score for.
    The function then calculates Cronbach's alpha for the indicators using the `cronbach_alpha` function from the `pingouin` package. Cronbach's alpha is a measure of internal consistency, i.e., how closely related a set of items are as a group.
    The function also calculates the average score, variance, and count for the indicators. It does this by first dropping any rows with missing values for the indicators, then calculating the mean and variance for each row, and finally calculating the mean, variance, and count for these values.
    The function returns a dictionary with the average score, standard deviation (calculated as the square root of the variance), count, and Cronbach's alpha for the indicators.
    """
    indikatorer = [
       'Jeg skjønner hvorfor jeg har mottatt dette brevet.',
       'Brevet får frem hva jeg kan eller må gjøre etter å ha lest det.',
       'Det var lett å finne den informasjonen i brevet som er viktigst for meg.',
       'Overskriftene i brevet forteller meg hva teksten handler om. ',
       'Jeg forstår alle ordene som er brukt i brevet.',
       'Brevet henvender seg direkte til meg som person.',
       'Brevet inneholder ingen skrivefeil. ',
       'Skriftstørrelsen i brevet passer meg.']

    alpha = pg.cronbach_alpha(data=df[indikatorer].dropna(axis = 0))
    df_out = df[indikatorer].dropna(axis = 0).agg(["mean", "var"], axis = 1).agg(["mean", "var", "count"])["mean"]

    return dict(Gjennomsnitt=df_out["mean"], 
                Standardavvik=np.sqrt(df_out["var"]),
                N=df_out["count"].astype("int64"), 
                Chronbachs_alpha = alpha[0])
    
    
    
    
def andel_tidsbruk(df):
    """_summary_

    Args:
        df (pd.DataFrame): Dataframe med all data
        int (_type_): antall som har besvart spørsmålet
        float (_type_): 

    Returns:
        _type_: _description_
    """
    q_tidsbruk = 'Hvor lang tid brukte du på å lese og forstå brevet? '
    #q_brevtype = 'Tenk på det siste brevet du fikk fra oss. Hva handlet brevet om?'


    df[q_tidsbruk] = df[q_tidsbruk].astype(
                     CategoricalDtype(categories=["Omtrent 5 minutter",
                                                  "Omtrent 15 minutter",
                                                  "Omtrent 30 minutter", 
                                                  "Omtrent 1 time",
                                                  "Mer enn 1 time"]
                                      , ordered=True)
    )

    #Tall output:
    N_svar = (~df[q_tidsbruk].isna()).sum()
    p_5pst = (df[q_tidsbruk].value_counts()["Omtrent 5 minutter"]/N_svar*100).round(1)

    ### Plotting
    fig = go.Figure()
    fig.add_trace(go.Bar( text=(df[q_tidsbruk].value_counts()/N_svar*100).round(1).astype(str) + "%" +  '<br>' + df[q_tidsbruk].value_counts().astype(str) + " svar",
             x =df[q_tidsbruk].value_counts().index,
             y = df[q_tidsbruk].value_counts()/N_svar*100) )#.update_layout(barmode='group')

    fig.update_traces(textfont_size=12, textangle=0, textposition="inside", cliponaxis=False)
    fig.add_annotation(x=4, y=50,
                text="Totalt antall svar: " + str(N_svar),
                showarrow=False,
                font_size = 18,# = dict(size = 18),
                yshift=10)
    fig.update_yaxes(ticksuffix="%")

    fig.update_layout(#barmode='group', 
                      template='plotly_white', 
                      #legend=dict(orientation='h', x=0.3), 
                      title={
                          'text': q_tidsbruk,
                          #'y':0.9,
                          #'x':0.5,
                          'xanchor': 'left',
                          'yanchor': 'top'}, bargroupgap=0.15)
    return fig, N_svar, p_5pst


def kontakt_NAV(df: pd.DataFrame) -> dict:
    antall_kontakt = df["Tok du kontakt med NAV for å få hjelp til å forstå brevet?"].value_counts()
    
    
    df.loc[(df["Hvem fikk du hjelp fra?"].str.rfind("Andre") +1).astype("boolean"), "Hvem fikk du hjelp fra?"] = "Andre"
    return antall_kontakt



def plott_skår_brevtype(df: pd.DataFrame) -> go.Figure:
    indikatorer = [
           'Jeg skjønner hvorfor jeg har mottatt dette brevet.',
           'Brevet får frem hva jeg kan eller må gjøre etter å ha lest det.',
           'Det var lett å finne den informasjonen i brevet som er viktigst for meg.',
           'Overskriftene i brevet forteller meg hva teksten handler om. ',
           'Jeg forstår alle ordene som er brukt i brevet.',
           'Brevet henvender seg direkte til meg som person.',
           'Brevet inneholder ingen skrivefeil. ',
           'Skriftstørrelsen i brevet passer meg.']
    #df = pd.read_csv("hotjar_clean.csv")
    q_brevtype = 'Tenk på det siste brevet du fikk fra oss. Hva handlet brevet om?'
    index_komplette_svar = df[indikatorer].dropna(axis = 0).index
    df_ = df.iloc[index_komplette_svar,:].copy(deep = True)

    df_brevtyper_skår = df_[indikatorer].agg(["mean"], axis = 1).groupby(df_[q_brevtype]).agg(["mean", "std",   "count"])
    df_brevtyper_skår["alpha"] = np.nan
    # Finne alpha
    for brevtype in df_[q_brevtype].unique():
        df_brevtyper_skår.loc[brevtype, "alpha"] =  pg.cronbach_alpha(df_.loc[df_[q_brevtype] == brevtype,  indikatorer])[0] 
    df_brevtyper_skår = df_brevtyper_skår.reset_index()
    df_brevtyper_skår.columns = pd.Index(["Brevtype", "Gjennomsnitt", "std", "N", "alpha"])


    fig = go.Figure()
    fig.add_trace(go.Bar(text= "Skår=" + df_brevtyper_skår["Gjennomsnitt"].round(1).astype(str) + "<br> <br>" +   
                                "N=" + df_brevtyper_skår["N"].astype(str) +  
                                '<br>' + u"\u03b1" + "=" + df_brevtyper_skår["alpha"].round(2).astype(str),
             x = df_brevtyper_skår["Brevtype"],
             y = df_brevtyper_skår["Gjennomsnitt"])
             #error_y=dict(type='data', array= df_brevtyper_skår["std"])
             )

    fig.update_traces(textfont_size=12, textangle=0, textposition="inside", cliponaxis=False)
    fig.add_annotation(x=4, y=5,
                text="Totalt antall svar: " + str(df_brevtyper_skår["N"].sum()),
                showarrow=False,
                font_size = 18,
                yshift=10)


    fig.update_layout(#barmode='group', 
                      template='plotly_white', 
                      #legend=dict(orientation='h', x=0.3), 
                      title={
                          'text': "Gjennomsnittlig skår for brevtyper, 1-5",
                          #'y':0.9,
                          #'x':0.5,
                          'xanchor': 'left',
                          'yanchor': 'top'}, bargroupgap=0.15)
    return fig


def plott_radar_faktorer(df):
    q_brevtype = 'Tenk på det siste brevet du fikk fra oss. Hva handlet brevet om?'
    indikatorer = [
               'Jeg skjønner hvorfor jeg har mottatt dette brevet.',
               'Brevet får frem hva jeg kan eller må gjøre etter å ha lest det.',
               'Det var lett å finne den informasjonen i brevet som er viktigst for meg.',
               'Overskriftene i brevet forteller meg hva teksten handler om. ',
               'Jeg forstår alle ordene som er brukt i brevet.',
               'Brevet henvender seg direkte til meg som person.',
               'Brevet inneholder ingen skrivefeil. ',
               'Skriftstørrelsen i brevet passer meg.']
    dict_faktorer = {
               'Funksjon': ['Jeg skjønner hvorfor jeg har mottatt dette brevet.',
               'Brevet får frem hva jeg kan eller må gjøre etter å ha lest det.']
               ,
               'Struktur': ['Det var lett å finne den informasjonen i brevet som er viktigst for meg.',
               'Overskriftene i brevet forteller meg hva teksten handler om. ']
               ,
               'Formuleringer':['Jeg forstår alle ordene som er brukt i brevet.',
               'Brevet henvender seg direkte til meg som person.']
               ,
               'Rettskriving':['Brevet inneholder ingen skrivefeil. '],
               'Utforming': ['Skriftstørrelsen i brevet passer meg.']}
    index_komplette_svar = df[indikatorer].dropna(axis = 0).index
    df_ = df.iloc[index_komplette_svar,:].copy(deep = True)
    df_faktorer_skår = pd.DataFrame({"Brevtype": sorted(list(df_[q_brevtype].unique())*len(dict_faktorer.keys())),
                                    "Faktorer":list(dict_faktorer.keys())*len(df_[q_brevtype].unique()),
                                    "Gjennomsnitt": np.nan,
                                    "std":np.nan,
                                    "alpha": np.nan,
                                    "N":np.nan})
   





    for brevtype in df_[q_brevtype].unique():
        for faktor in dict_faktorer.keys():
            rad_index = ((df_faktorer_skår.Faktorer == faktor) & (df_faktorer_skår.Brevtype == brevtype))
            if (len(dict_faktorer[faktor]) < 2):
                alpha = np.nan
            elif (len(dict_faktorer[faktor]) >= 2):
                alpha = pg.cronbach_alpha((df_.loc[df_[q_brevtype] == brevtype,  dict_faktorer[faktor]]))[0] 

            df_faktorer_skår.loc[rad_index,["Gjennomsnitt"]] = df_.loc[df_[q_brevtype] == brevtype,  dict_faktorer[faktor]].mean(axis = 1).mean().round(2)
            df_faktorer_skår.loc[rad_index,["std"]] = df_.loc[df_[q_brevtype] == brevtype,  dict_faktorer[faktor]].mean(axis = 1).std()
            df_faktorer_skår.loc[rad_index,["alpha"]] = alpha
            df_faktorer_skår.loc[rad_index,["N"]] = df_.loc[df_[q_brevtype] == brevtype,  dict_faktorer[faktor]].mean(axis = 1).count()

    #df_faktorer_skår = df_faktorer_skår.sort_values(["Brevtype", "Gjennomsnitt"])


    fig = go.Figure()
    for brevtype in df_[q_brevtype].unique():
        df_plot = pd.concat([df_faktorer_skår.loc[df_faktorer_skår["Brevtype"] == brevtype,:], df_faktorer_skår.loc[df_faktorer_skår["Brevtype"] == brevtype,:].iloc[0].to_frame().T], axis = 0)
        fig.add_trace(go.Scatterpolar(
                        r=df_plot["Gjennomsnitt"],
                        theta=df_plot["Faktorer"],
                        fill=None,
                        name=list((df_plot["Brevtype"] +", N=" + df_plot["N"].astype("int64").astype(str)))[1],
                        #marker_symbol = df_plot["Brevtype"]
                        hovertemplate='Gjennomsnitt: %{r} <br>Faktor: %{theta} '
                        ))
        
        
    
    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
          range=[1, 5],
          ticks = "outside",
          tickvals = [1, 2, 3, 4, 5],
          hoverformat = "r unified"
        )),
        #hovermode = "unified",
        legend=dict(
                    orientation="v",
                    yanchor="bottom",
                    y=0.0,
                    xanchor="left",
                    x=0
                    ),
      showlegend=True
    )
    


    
    
    #fig.update_layout()

    return fig 
    
# %%
