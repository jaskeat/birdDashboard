import streamlit as st
import pandas as pd
import requests
import pydeck as pdk 

def getApiKey():
    try:
        return st.secrets["ApiKey"]
    except (KeyError, FileNotFoundError):
        from dotenv import load_dotenv
        import os
        load_dotenv(".env")
        return os.getenv("ApiKey") 
        
def fetchRecent(apiKey,type):
    if type=="API":
        try:
            regionCode = "HK"
            url = f"https://api.ebird.org/v2/data/obs/{regionCode}/recent"

            r = requests.get(url,headers={"X-eBirdApiToken":apiKey})
            
            df = pd.DataFrame(r.json())
            return df
        except Exception as e:
            st.error(f"Error: {e}")
            return None
    elif type=="CSV":
        try:
            df = pd.read_csv("./data/data.csv")
            return df
        except Exception as e:
            st.error(f"Error: {e}")
            return None
        
def fetchHotspot(apiKey,type):
    if type=="API":
        return
    elif type=="CSV":
        try:
            df = pd.read_csv("./data/data.csv")
            return df
        except Exception as e:
            st.error(f"Error: {e}")
            return None
        
    

def main():
    st.title("Hong Kong Bird Sighting Dashboard")
    
    apiKey = getApiKey()
    apiKey = "d"
    
    if not apiKey:
        st.error("apiKey not found. Add it to Streamlit secrets or .env file.")
        st.stop()
    
    if "df" not in st.session_state:
        st.session_state.df = None

    # Show loading prompt if no data loaded
    if st.session_state.df is None:
        st.text("No data has been loaded")
        fetch = st.button("Load data")
        
        if fetch:
            try:
                with st.spinner("Calling API"):
                    st.session_state.df = fetchRecent(apiKey,"CSV")
                    st.rerun()
            except Exception as e:
                st.write(f"Error: {e}")
    
    # Retrieve data from session state
    df = st.session_state.df
    
    # Layout for map and recent sightings
    col1, col2 = st.columns([2, 1])  # Create two columns, one wider than the other

    with col1:
        # Showing heatmap      
        if df is not None:
            #TODO: ADD IT SO WHEN U CLICK ON THE POINT, IT OPENS IT IN GOOGLE MAPS
            st.header("Recent Species Sighting")      
            st.caption("Hover to see location and bird name")  
            df['calculated_field'] = df['locRowCount'] / 35  # Create a new column for the calculated field
            st.pydeck_chart(
                pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(
                latitude=df["lat"].mean(),
                longitude=df["lon"].mean(),
                zoom=10,
                ),
                layers=[
                pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position='[lon, lat]',
                get_radius=400,
                get_fill_color="[255, 0, 0]",
                pickable=True,
                )
                ],
                tooltip={"text": "{locName} \n {comName}"},
                )
            )

    with col2:
        # Showing recent sightings
        if df is not None:
            # st.header("Recent bird sightings")
            recentFive = df.head(4)
            for row in recentFive.iterrows():
                c = st.container(border=True)
                c.write(row[1]["comName"])
                c.caption(row[1]["locName"])
                c.caption(row[1]["obsDt"])
                
    with col1:
        st.header("Hong Kong Hotspots")


        
main()