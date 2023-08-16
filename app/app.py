import streamlit as st 
import pandas as pd
import requests

st.set_page_config(
    page_title="Weather Track",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded",
)

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True
    
def getData(lat, lon, date=None, data="temperature_2m,precipitation,rain,temperature_80m,temperature_120m,temperature_180m"):
    #https://archive-api.open-meteo.com/v1/era5?latitude=52.52&longitude=13.41&start_date=2021-01-01&end_date=2021-12-31&hourly=temperature_2m
    r = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={data}&past_days=92")
    d = r.json()
    df = pd.DataFrame(d["hourly"])
    df['time'] = pd.to_datetime(df['time'])


    # Convert the target string to datetime
    target_datetime = pd.to_datetime(date)

    # Compute the absolute difference with each datetime in the 'Date' column
    time_diffs = abs(df['time'] - target_datetime)

    # Find the index of the smallest difference
    closest_index = time_diffs.idxmin()

    # Retrieve the corresponding row
    closest_row = df.loc[closest_index]

    return closest_row

def downloadCSV(df):
    csv = df.to_csv(index=False)
    # Convert the CSV string to bytes
    b_csv = csv.encode()
    return b_csv

def extendDF(df1,df2):
    return  pd.concat([df1.reset_index(drop=True), df2.reset_index(drop=True)], axis=1)


if check_password():
    st.write("# Weather Track")
    st.write("Load the CSV with the coordinates and dates and click load.")

    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.sidebar.write("Loaded")
        except Exception as e:
            st.sidebar.write("Oops! There was an error: ", e)
    
    loadB = st.sidebar.button("1-Load")   
    weatherData = st.sidebar.button("2-Get Weather Data")
    #download = st.sidebar.button("3-Download Weather Data CSV")
    # Use the streamlit download button to offer the CSV for download

    #plotMap =st.sidebar.button("Opt1-Plot Map")
    #plotTemp = st.sidebar.button("Opt2-Plot Temperature")



    ## show table stgrid

    if loadB:
        st.dataframe(df)
        

    if weatherData:
        # ############
        st.dataframe(df)
        st.markdown("""---""")
        st.write("Fetching the data. Patience, this can take a while :)")
        ########################

        weatherData = []
        for i, v in df.iterrows():
            lat = v["Latitude"]
            lon = v["Longitude"]
            date = v["UTC_datetime"]

            output = getData(lat, lon, date=date)
            weatherData.append(output)

        df_concatenated = pd.concat(weatherData, axis=1).transpose()
        st.dataframe(df_concatenated)

        st.line_chart(data=df_concatenated, x="time", y="temperature_2m")

        st.sidebar.download_button(
            label="Opt3-Download ExtendedCSV",
            data=downloadCSV(extendDF(df, df_concatenated)),
            file_name="extendedDataframe.csv",
            mime="text/csv")
        
        st.sidebar.download_button(
            label="3-Download CSV",
            data=downloadCSV(df),
            file_name="dataframe.csv",
            mime="text/csv")


    # if plotTemp:
    #     st.dataframe(df)
    #     st.markdown("""---""")
    #     st.dataframe(df_concatenated)
    #     st.line_chart(df_concatenated)


st.write("Weather Track. 2023. By Vivar Rios Analytics. carlosvivarrios@gmail.com")