# %%
import pandas as pd

# %%
xlsx = pd.ExcelFile("../hotjar brev endelig versjon.xlsx")
# %%
sheets = xlsx.sheet_names  # sheet names
sheets.remove("Oppsummering")
sheets.remove("Sheet1")


# %%
def merge_sheets(data) -> pd.DataFrame:
    """
    Merge a list of sheets from an excel workbook, and keep only the data that matches the criteria
    """
    list_sheet_frames = []
    for sheet in sheets:
        data = pd.read_excel(xlsx, sheet)
        data[
            "Har du nylig mottatt brev fra oss? Vil du svare på en 5 minutters spørreundersøkelse om brevet?"
        ] = data[
            "Har du nylig mottatt brev fra oss? Vil du svare på en 5 minutters spørreundersøkelse om brevet?"
        ].replace(
            to_replace="  ", value="Ja"
        )
        _ = data[
            data[
                "Har du nylig mottatt brev fra oss? Vil du svare på en 5 minutters spørreundersøkelse om brevet?"
            ]
            == "Ja"
        ]
        list_sheet_frames.append(_)
    dfs = pd.concat(list_sheet_frames)
    return dfs


dfs = merge_sheets(data=xlsx)

# drop unnamed cols
_ = [s for s in dfs.columns if "Unnamed" in s]
for i in _:
    dfs.drop(columns=i, inplace=True)
dfs.to_excel("../ny_oppsummering.xlsx", index=False, sheet_name="data_vasket")

# %%
