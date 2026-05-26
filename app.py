import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

from database import init_db
from sql_queries import get_animal_summary


# ----------------------------
# Movement anomaly detection
# ----------------------------
def detect_anomalies(df):
    df = df.sort_values(["animal_id", "timestamp"]).copy()

    df["prev_lat"] = df.groupby("animal_id")["latitude"].shift()
    df["prev_lon"] = df.groupby("animal_id")["longitude"].shift()

    df["distance"] = np.sqrt(
        (df["latitude"] - df["prev_lat"])**2 +
        (df["longitude"] - df["prev_lon"])**2
    )

    anomalies = df[df["distance"] > 0.1]
    return anomalies


# ----------------------------
# Load data from database
# ----------------------------
conn = init_db()
df = pd.read_sql("SELECT * FROM wildlife_raw", conn)

# ----------------------------
# UI Setup
# ----------------------------
st.title("Wildlife Movement Data Explorer")
st.subheader("Colorado Wildlife GPS Tracking Dashboard")

# ----------------------------
# Sidebar filter
# ----------------------------
animals = df["animal_id"].unique()
selected_animal = st.sidebar.selectbox("Select Animal", animals)

filtered_df = df[df["animal_id"] == selected_animal]

# ----------------------------
# Detect anomalies
# ----------------------------
anomalies_df = detect_anomalies(filtered_df)

# safer split (avoids index issues)
normal_df = filtered_df[~filtered_df.index.isin(anomalies_df.index)]

# ----------------------------
# Debug (optional but helpful)
# ----------------------------
st.write("Normal rows:", len(normal_df))
st.write("Anomaly rows:", len(anomalies_df))

# ----------------------------
# Raw data view
# ----------------------------
st.write("### Raw GPS Data")
st.dataframe(filtered_df)

# ----------------------------
# Map visualization (normal + anomalies)
# ----------------------------
st.write("### Movement Map (Normal vs Anomalies)")

if len(filtered_df) == 0:
    st.warning("No data available for selected animal.")
else:
    fig = px.scatter_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        color_discrete_sequence=["green"],
        zoom=6,
        height=500
    )

    fig.update_layout(mapbox_style="open-street-map")

    if len(anomalies_df) > 0:
        fig.add_scattermapbox(
            lat=anomalies_df["latitude"],
            lon=anomalies_df["longitude"],
            mode="markers",
            marker=dict(size=10, color="red"),
            name="Anomalies"
        )

    st.plotly_chart(fig)

# ----------------------------
# Movement path (trail)
# ----------------------------
st.write("### Movement Path")

if len(filtered_df) > 0:
    fig2 = px.line_mapbox(
        filtered_df.sort_values("timestamp"),
        lat="latitude",
        lon="longitude",
        zoom=6,
        height=400
    )

    fig2.update_layout(mapbox_style="open-street-map")

    st.plotly_chart(fig2)

# ----------------------------
# Summary stats (SQL layer)
# ----------------------------
st.write("### Animal Movement Summary")

summary = get_animal_summary(conn)
st.dataframe(summary)

# ----------------------------
# Data quality overview
# ----------------------------
st.write("### Data Quality Overview")

st.metric("Total Records", len(df))
st.metric("Animals Tracked", len(animals))
