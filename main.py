import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import requests
    from dotenv import load_dotenv
    import os
    from io import StringIO
    return StringIO, load_dotenv, mo, os, pd, requests


@app.cell
def _(load_dotenv, os):
    load_dotenv('.env')

    apiKey = os.getenv('apiKey')
    print(apiKey)
    return (apiKey,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Recent Observations""")
    return


@app.cell
def _(apiKey, requests):
    regionCode = "HK"
    url = f"https://api.ebird.org/v2/data/obs/{regionCode}/recent"

    r = requests.get(url,headers={"X-eBirdApiToken":apiKey})
    print(r.status_code)
    return r, regionCode


@app.cell
def _(r):
    r.json()
    return


@app.cell
def _(pd, r):
    df = pd.DataFrame(r.json())
    df 
    return (df,)


@app.cell
def _(df, pd):
    df["obsDt"] = pd.to_datetime(df["obsDt"])
    df
    return


@app.cell
def _(df):
    df.info()
    return


@app.cell
def _(df):
    df.rename(columns={'lng':'lon'}, inplace=True)
    df["locRowCount"] = df.groupby("locId")["locId"].transform("size") * 35
    df["locRowCount"] = df["locRowCount"].clip(lower=600)
    df
    return


@app.cell
def _(df):
    df.to_csv("./data/data.csv")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Hotspots""")
    return


@app.cell
def _(apiKey, regionCode, requests):
    def _():
        url = f"https://api.ebird.org/v2/ref/hotspot/{regionCode}"

        r = requests.get(url,headers={"X-eBirdApiToken":apiKey})
        return r

    hotspotR = _()

    hotspotR.status_code
    return (hotspotR,)


@app.cell
def _(hotspotR):
    hotspotR.text
    return


@app.cell
def _(StringIO, hotspotR, pd):
    hotspot_df = pd.read_csv(StringIO(hotspotR.text), header=None, names=['locId', 'countryCode', 'subnational1Code', 'subnational2Code', 'lat', 'lon', 'locName', 'obsDt', 'numObservations', 'numSpeciesLastMonth'])
    hotspot_df
    return (hotspot_df,)


@app.cell
def _(hotspot_df):
    hotspot_df.info()
    return


@app.cell
def _(hotspot_df, pd):
    hotspot_df["obsDt"] = pd.to_datetime(hotspot_df["obsDt"])
    hotspot_df.sort_values(by="obsDt",ascending=False,inplace=True)
    hotspot_df
    return


@app.cell
def _(hotspot_df):
    hotspot_df.info()
    return


@app.cell
def _(hotspot_df):
    hotspot_df.to_csv('./data/hotspot.csv')
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
