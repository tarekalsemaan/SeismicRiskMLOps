import os
from datetime import datetime

import folium
import requests
import streamlit as st
from streamlit_folium import st_folium


# ============================================================
# Configuration
# ============================================================

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8001/predict"
)

DEFAULT_DEPTH_KM = 20.0

TECTONIC_BOUNDARIES_URL = (
    "https://raw.githubusercontent.com/fraxen/"
    "tectonicplates/master/GeoJSON/PB2002_boundaries.json"
)


# ============================================================
# Session state
# ============================================================

if "selected_latitude" not in st.session_state:
    st.session_state.selected_latitude = None

if "selected_longitude" not in st.session_state:
    st.session_state.selected_longitude = None

if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None


# ============================================================
# Page
# ============================================================

st.set_page_config(
    page_title="Risque sismique - MLOps",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Risque sismique - MLOps")

st.write(
    "Sélectionnez une date et une heure, puis cliquez sur la carte mondiale. "
    "Le modèle H2O classe automatiquement le scénario sismique associé."
)

st.info(
    "Cette application classe un scénario sismique. "
    "Elle ne prédit pas où ni quand un futur séisme se produira."
)


# ============================================================
# Date and time
# ============================================================

col_date, col_time = st.columns(2)

with col_date:
    selected_date = st.date_input(
        "📅 Date de l'événement",
        value=datetime.utcnow().date()
    )

with col_time:
    selected_time = st.time_input(
        "🕒 Heure UTC",
        value=datetime.utcnow().time().replace(
            minute=0,
            second=0,
            microsecond=0
        )
    )


month = selected_date.month
day = selected_date.day
hour = selected_time.hour
day_of_week = selected_date.weekday()


# ============================================================
# Build map
# ============================================================

st.subheader("🗺️ Cliquez sur la carte")

st.caption(
    "Les lignes rouges représentent les limites tectoniques PB2002."
)

world_map = folium.Map(
    location=[20, 0],
    zoom_start=2,
    tiles="OpenStreetMap",
    control_scale=True
)

folium.GeoJson(
    TECTONIC_BOUNDARIES_URL,
    name="Limites tectoniques",
    style_function=lambda feature: {
        "color": "#ff3b30",
        "weight": 2,
        "opacity": 0.85
    }
).add_to(world_map)


# ============================================================
# Existing prediction marker
# ============================================================

if (
    st.session_state.selected_latitude is not None
    and st.session_state.selected_longitude is not None
):

    lat = st.session_state.selected_latitude
    lon = st.session_state.selected_longitude

    result = st.session_state.prediction_result

    if result is not None:

        strong_pct = result["probability_strong"] * 100
        threshold_pct = result["decision_threshold_percent"]

        if result["strong_earthquake"]:
            classification = "⚠️ Séisme fort"
        else:
            classification = "✅ Séisme non fort"

        popup_text = (
            f"<b>{classification}</b><br><br>"
            f"Latitude : {lat:.4f}<br>"
            f"Longitude : {lon:.4f}<br>"
            f"Probabilité forte : {strong_pct:.2f}%<br>"
            f"Seuil : {threshold_pct:.2f}%"
        )

    else:

        popup_text = (
            "<b>Position sélectionnée</b><br>"
            f"Latitude : {lat:.4f}<br>"
            f"Longitude : {lon:.4f}"
        )

    marker = folium.Marker(
        [lat, lon],
        popup=folium.Popup(
            popup_text,
            max_width=350
        ),
        tooltip="Cliquez pour voir le résultat"
    )

    marker.add_to(world_map)


folium.LayerControl().add_to(world_map)


# ============================================================
# Interactive map
# ============================================================

map_data = st_folium(
    world_map,
    width=None,
    height=600,
    returned_objects=["last_clicked"],
    key="main_map"
)


# ============================================================
# Detect new click
# ============================================================

if map_data and map_data.get("last_clicked"):

    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lon = map_data["last_clicked"]["lng"]

    old_lat = st.session_state.selected_latitude
    old_lon = st.session_state.selected_longitude

    is_new_click = (
        old_lat is None
        or old_lon is None
        or abs(clicked_lat - old_lat) > 0.000001
        or abs(clicked_lon - old_lon) > 0.000001
    )

    if is_new_click:

        st.session_state.selected_latitude = clicked_lat
        st.session_state.selected_longitude = clicked_lon

        payload = {
            "latitude": clicked_lat,
            "longitude": clicked_lon,
            "depth": DEFAULT_DEPTH_KM,
            "month": month,
            "day": day,
            "hour": hour,
            "day_of_week": day_of_week
        }

        try:

            with st.spinner("Analyse du scénario..."):

                response = requests.post(
                    API_URL,
                    json=payload,
                    timeout=30
                )

            if response.status_code == 200:

                st.session_state.prediction_result = response.json()

                st.rerun()

            else:

                st.session_state.prediction_result = None

                st.error(
                    f"Erreur API : {response.status_code}"
                )

                st.code(response.text)

        except Exception as e:

            st.session_state.prediction_result = None

            st.error(
                f"Impossible de communiquer avec FastAPI : {e}"
            )


# ============================================================
# Persistent result below map
# ============================================================

result = st.session_state.prediction_result

latitude = st.session_state.selected_latitude
longitude = st.session_state.selected_longitude


if (
    result is not None
    and latitude is not None
    and longitude is not None
):

    strong_pct = result["probability_strong"] * 100
    not_strong_pct = result["probability_not_strong"] * 100
    threshold_pct = result["decision_threshold_percent"]

    st.divider()

    st.success("✅ Prédiction terminée")

    st.write(
        f"📍 Position : {latitude:.4f}, {longitude:.4f}"
    )

    st.write(
        f"📅 {selected_date.strftime('%Y-%m-%d')} "
        f"— 🕒 {hour:02d}:00 UTC"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Probabilité de séisme fort",
            f"{strong_pct:.2f}%"
        )

    with col2:
        st.metric(
            "Probabilité de séisme non fort",
            f"{not_strong_pct:.2f}%"
        )

    with col3:
        st.metric(
            "Seuil de décision",
            f"{threshold_pct:.2f}%"
        )


    if result["strong_earthquake"]:

        st.warning(
            "⚠️ Classification : séisme fort"
        )

        st.write(
            f"{strong_pct:.2f}% est supérieur "
            f"au seuil de {threshold_pct:.2f}%."
        )

    else:

        st.info(
            "ℹ️ Classification : séisme non fort"
        )

        st.write(
            f"{strong_pct:.2f}% est inférieur "
            f"au seuil de {threshold_pct:.2f}%."
        )


    st.caption(
        "La profondeur n'est pas demandée à l'utilisateur. "
        f"Le modèle utilise actuellement une valeur interne "
        f"de {DEFAULT_DEPTH_KM:.0f} km."
    )

    st.caption(
        "La classification concerne uniquement le scénario sélectionné. "
        "Elle ne signifie pas qu'un futur séisme se produira à cet endroit."
    )

else:

    st.warning(
        "👆 Cliquez sur un emplacement de la carte pour lancer la prédiction."
    )