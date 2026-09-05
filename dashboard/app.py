import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001/predict"

st.set_page_config(
    page_title="Seismic Risk Dashboard",
    layout="centered"
)

st.title("Seismic Risk Dashboard")
st.write(
    "Enter earthquake characteristics and let the H2O model classify "
    "whether the recorded event belongs to the strong-earthquake class."
)

latitude = st.number_input("Latitude", value=35.0)
longitude = st.number_input("Longitude", value=140.0)
depth = st.number_input("Depth (km)", value=20.0)

month = st.number_input("Month", min_value=1, max_value=12, value=9)
day = st.number_input("Day", min_value=1, max_value=31, value=4)
hour = st.number_input("Hour (UTC)", min_value=0, max_value=23, value=12)
day_of_week = st.number_input("Day of week", min_value=0, max_value=6, value=4)

if st.button("Predict"):

    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "depth": depth,
        "month": month,
        "day": day,
        "hour": hour,
        "day_of_week": day_of_week
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            strong_pct = result["probability_strong"] * 100
            not_strong_pct = result["probability_not_strong"] * 100
            threshold_pct = result["decision_threshold_percent"]

            st.success("Prediction completed")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Strong probability",
                    f"{strong_pct:.2f}%"
                )

            with col2:
                st.metric(
                    "Not-strong probability",
                    f"{not_strong_pct:.2f}%"
                )

            st.metric(
                "Decision threshold",
                f"{threshold_pct:.2f}%"
            )

            if result["strong_earthquake"]:
                st.warning("Classification: Strong earthquake")
                st.write(
                    f"Reason: {strong_pct:.2f}% is above the "
                    f"{threshold_pct:.2f}% decision threshold."
                )
            else:
                st.info("Classification: Not strong earthquake")
                st.write(
                    f"Reason: {strong_pct:.2f}% is below the "
                    f"{threshold_pct:.2f}% decision threshold."
                )

            st.caption(
                "This model classifies a recorded earthquake event. "
                "It does not predict when or where a future earthquake will occur."
            )

        else:
            st.error(f"API error: {response.status_code}")

    except Exception as e:
        st.error(f"Could not connect to FastAPI: {e}")
