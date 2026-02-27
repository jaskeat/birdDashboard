import streamlit as st
import pandas as pd
import requests
import pydeck as pdk 

st.set_page_config(layout="wide", page_title="Bird Dashboard")


def getApiKey():
    # If the file is on your local machine, you need to 
    # create a secrets.toml or a .env file with the API Key

    if "ApiKey" in st.secrets:
        return st.secrets["ApiKey"]
    else:
        from dotenv import load_dotenv
        import os
        load_dotenv(".env")
        return os.getenv("ApiKey")
       
# Fetch functions:
# Type == "CSV" is for when wanting to test the app but you do not want to make
# too many calls so it uses the csv on your device

def fetchRecentDf(apiKey,type):
    if type=="API":
        try:
            regionCode = "HK"
            url = f"https://api.ebird.org/v2/data/obs/{regionCode}/recent"
            r = requests.get(url, headers={"X-eBirdApiToken": apiKey})
            if r.status_code != 200:
                st.error(f"API Error {r.status_code}: {r.text}")
                print(f"API Error {r.status_code}: {r.text}")
                return None
            try:
                df = pd.DataFrame(r.json())
                return df
            except Exception as e:
                st.error(f"JSON decode error: {e}\nResponse: {r.text}")
                print(f"JSON decode error: {e}\nResponse: {r.text}")
                return None
        except Exception as e:
            st.error(f"Error: {e}")
            print(f"fetchRecentDf Error: {e}")
            return None
    elif type=="CSV":
        try:
            df = pd.read_csv("./data/data.csv")
            df['obsDt'] = pd.to_datetime(df['obsDt'])
            return df
        except Exception as e:
            st.error(f"Error: {e}")
            return None
        
def fetchNotableDf(apiKey,type):
    if type=="API":
        try:
            regionCode = "HK"
            url = f"https://api.ebird.org/v2/data/obs/{regionCode}/recent/notable?detail=full"
            r = requests.get(url, headers={"X-eBirdApiToken": apiKey})
            if r.status_code != 200:
                st.error(f"API Error {r.status_code}: {r.text}")
                print(f"API Error {r.status_code}: {r.text}")
                return None
            try:
                notabledf = pd.DataFrame(r.json())
                notabledf = notabledf.drop_duplicates(subset="obsDt", keep="first")
                if "obsReviewed" in notabledf.columns:
                    notabledf = notabledf[notabledf["obsReviewed"] == True]
                notabledf["obsDt"] = pd.to_datetime(notabledf["obsDt"])
                return notabledf
            except Exception as e:
                st.error(f"JSON decode error: {e}\nResponse: {r.text}")
                print(f"JSON decode error: {e}\nResponse: {r.text}")
                return None
        except Exception as e:
            st.error(f"Error: {e}")
            print(f"fetchNotabletDf Error: {e}")
            return None
    elif type=="CSV":
        try:
            df = pd.read_csv("./data/notable.csv")
            return df
        except Exception as e:
            st.error(f"Error: {e}")
            return None 
        
def fetchHotspotDf(apiKey,type):
    if type=="API":
        try:
            regionCode = "HK"
            url = f"https://api.ebird.org/v2/ref/hotspot/{regionCode}"
            r = requests.get(url, headers={"X-eBirdApiToken": apiKey})
            from io import StringIO
            hotspot_df = pd.read_csv(StringIO(r.text), header=None, names=[
                'locId', 'countryCode', 'subnational1Code', 'subnational2Code', 'lat', 'lon', 'locName', 'obsDt', 'numObservations', 'numSpeciesLastMonth'])
            hotspot_df["obsDt"] = pd.to_datetime(hotspot_df["obsDt"])
            hotspot_df.sort_values(by="obsDt", ascending=False, inplace=True)
            return hotspot_df
        except Exception as e:
            st.error(f"Error: {e}")
            return None
    elif type=="CSV":
        try:
            df = pd.read_csv("./data/hotspot.csv")
            df['obsDt'] = pd.to_datetime(df['obsDt'])
            return df
        except Exception as e:
            st.error(f"Error: {e}")
            return None
        
def filterDf(text,df):
    filteredDf = df[df["comName"].str.lower().str.contains(text, na=False)]
    return filteredDf

def main():
    st.title("Hong Kong Bird Sighting Dashboard")
    
    apiKey = getApiKey()
    print(apiKey)
    
    if not apiKey:
        st.error("apiKey not found. Add it to Streamlit secrets or .env file.")
        st.stop()
    
    if "df" not in st.session_state:
        st.session_state.df = None
        
    if "hotspotDf" not in st.session_state:
        st.session_state.hotspotDf = None

    if "notableDf" not in st.session_state:
        st.session_state.notableDf = None
     
    if st.session_state.df is None:
        st.text("No data has been loaded")
        fetch = st.button("Load data")
        
        if fetch:
            try:
                with st.spinner("Calling API"):
                    st.session_state.df = fetchRecentDf(apiKey,"API")
                    
                    if st.session_state.hotspotDf is None:
                        try:
                            st.session_state.hotspotDf = fetchHotspotDf(apiKey,"API")
                        except Exception as e:
                            st.write(f"Error with hotspot: {e}")
                            
                    if st.session_state.notableDf is None:
                        try:
                            st.session_state.notableDf = fetchNotableDf(apiKey,"API")
                        except Exception as e:
                            st.write(f"Error with notable: {e}")
                    st.rerun()
            except Exception as e:
                st.write(f"Error: {e}")

            
    df = st.session_state.df
    hotspotDf = st.session_state.hotspotDf
    notableDf = st.session_state.notableDf
    
    if df is not None and hotspotDf is not None:
        # Metrics row
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        metric_col1.metric("Top Hotspot", hotspotDf.loc[hotspotDf['numSpeciesLastMonth'].idxmax(), 'locName'],width="content")
        metric_col4.metric("Total Species", df['comName'].nunique())
        metric_col2.metric("Total Observations", df['howMany'].sum())
        metric_col3.metric("Active Hotspots", hotspotDf['locId'].nunique())
    
    # Main content layout
    col_map, col_list = st.columns([2, 1])
    
    with col_list:
        if df is not None:
            st.subheader("Recent bird sightings")
            st.caption("Scroll to see all sightings")
            show_notable = st.checkbox("Show only notable sightings", value=False)
            if show_notable:
                notableDf = st.session_state.notableDf
                if notableDf is not None:
                    searchText = st.text_input(
                        "Bird search (notable)",
                        key="notable_search",
                    )
                    filteredDf = filterDf(searchText.lower(), notableDf)
                    with st.container(height=700, border=False):
                        for row in filteredDf.iterrows():
                            c = st.container(border=True)
                            c.write(row[1]["comName"])
                            c.caption(row[1]["locName"])
                            c.caption(row[1]["obsDt"])
                else:
                    st.write("No notable sightings loaded.")
            else:
                searchText = st.text_input(
                    "Bird search",
                    key="placeholder",
                )
                filteredDf = filterDf(searchText.lower(), df)
                with st.container(height=700, border=False):
                    for row in filteredDf.iterrows():
                        c = st.container(border=True)
                        c.write(row[1]["comName"])
                        c.caption(row[1]["locName"])
                        c.caption(row[1]["obsDt"])
    
    with col_map:
        if hotspotDf is not None:
            last_date = hotspotDf['obsDt'].max().date()
            result = hotspotDf[hotspotDf['obsDt'].dt.date == last_date]
            result['radius'] = result['numObservations']*2
            st.subheader("Hong Kong Hotspots")
            
            st.caption(f"Bird observation hotspots on the date: {last_date}")  
            st.pydeck_chart(
                pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(
                latitude=result["lat"].mean(),
                longitude=result["lon"].mean(),
                zoom=10,
                ),
                layers=[
                pdk.Layer(
                "ScatterplotLayer",
                data=result,
                get_position='[lon, lat]',
                get_radius='radius',
                get_fill_color="[255, 0, 0]",
                pickable=True,
                )
                ],
                tooltip={"text": "{locName}"},
                )
            )

        
    with col_map:
        if hotspotDf is not None:
            st.subheader("Most diverse hotspots")
            if df is not None:
                location_diversity = df.groupby('locName').agg({
                    'comName': 'nunique',
                }).rename(columns={'comName': 'Species Count'})
                location_diversity = location_diversity.sort_values('Species Count', ascending=False)
                st.bar_chart(location_diversity.head(5))
            else:
                st.write("No data available to show hotspot diversity.")
main()