import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import streamlit.components.v1 as components
import datetime
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt


# Load data

@st.cache_data
def load_data():
    df = pd.read_csv("data/May_2025.csv")
    df.columns = df.columns.str.strip()

    # Reload 'Response Time' and convert to seconds from its initial format (assume HH:MM:SS)
    def response_time_to_seconds(rt):
        if pd.isna(rt) or rt == "":
            return 0
        try:
            t = pd.to_datetime(rt, format="%H:%M:%S", errors="coerce")
            if pd.isnull(t):
                return 0
            return t.hour * 3600 + t.minute * 60 + t.second
        except Exception:
            return 0

    df["Response Time (seconds)"] = df["Response Time"].apply(response_time_to_seconds)

    # Convert time columns to datetime, minutes, and seconds
    time_columns = ['Date/Time Created', 'Dispatched', 'Enroute', 'Staged', 'On Scene',
                    '1st Unit Arrived', 'Depart Scene', 'Cleared', 'At Hospital']
    for col in time_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # Retain the incident call dataframe (unique Incident #)
    incident_call_df = df.drop_duplicates(subset=['Incident #'])

    # Retain the unit response dataframe (all rows)
    unit_response_df = df.copy()

    return incident_call_df, unit_response_df

# Main sidebar for Navigation
st.sidebar.header("Navigation 🚒")
page = st.sidebar.selectbox("Select Page", [
    "Home",
    "Station Analytics",
    "Battalion Analytics",
    "County Analytics"
])

# Welcome Page
if page == "Home":
    st.markdown(
        """
        <h1 style='text-align: center; font-family: Arial, sans-serif; color: #FF0000;'>
            Prince George's County Fire & EMS Department 🚒🔥
        </h1>
        <h3 style='text-align: center; font-family: Georgia, serif; color: #333333;'>
            Welcome to the PGFD Data Analytics Dashboard 🔔
        </h3>
        <p style='font-family: Verdana, sans-serif; font-size: 16px; text-align: center;'>
            <b>Purpose:</b> This dashboard provides comprehensive analytics for the Prince George's County Fire & EMS Department, 
            visualizing incidents and unit responses across specific locations fire stations. 
            Explore incident locations, call demand patterns, call type distributions, response times, and others which aim to support 
            operational planning and resource allocation. 🚑📊
        </p>
        <h4 style='font-family: Arial, sans-serif; color: #333333; text-align: center;'>
            Contact Details 📞
        </h4>
        <p style='font-family: Verdana, sans-serif; font-size: 14px; text-align: center;'>
            <b>Prince George's County Fire/EMS Department</b><br>
            9201 Basil Court, Suite 452, Largo, MD 20774<br>
            Phone: (301) 883-5200<br>
            Email: pgfdpio@co.pg.md.us
        </p>
        <h4 style='font-family: Arial, sans-serif; color: #333333; text-align: center;'>
            Follow Us on Social Media 🌐
        </h4>
        <p style='font-family: Verdana, sans-serif; font-size: 14px; text-align: center;'>
            <a href='https://twitter.com/PGFDPIO'>Twitter</a> | 
            <a href='https://www.facebook.com/PGFD911'>Facebook</a> | 
            <a href='https://www.instagram.com/pgfdpio/'>Instagram</a>
        </p>
        """,
        unsafe_allow_html=True
    )

# Analytics Pages
# Part a: Incident calls per week, day, hour
st.subheader("Incident Calls Analysis", divider=True)
col1, col2, col3 = st.columns(3)

# Calculate average incident calls per week, day, and hour for May (4 weeks, 31 days, 744 hours)
incident_call_df, unit_response_df = load_data()
total_incidents = len(incident_call_df)
avg_per_week = total_incidents / 4
avg_per_day = total_incidents / 31
avg_per_hour = total_incidents / 744

with col1:
    st.metric("_Incidents per Week_", f"{avg_per_week:.0f}")

with col2:
    st.metric("_Incidents per Day_", f"{avg_per_day:.1f}")

with col3:
    st.metric("_Incidents per Hour_", f"{avg_per_hour:.1f}")

# Unit Responses Analysis per week, day, hour
st.subheader("Unit Responses Analysis", divider = "red")
col1, col2, col3 = st.columns(3)

# Calculate average unit responses per week, day, and hour for May (4 weeks, 31 days, 744 hours)
total_unit_responses = len(unit_response_df)
avg_unit_per_week = total_unit_responses / 4
avg_unit_per_day = total_unit_responses / 31
avg_unit_per_hour = total_unit_responses / 744

with col1:
    st.metric("_Unit Responses per Week_", f"{avg_unit_per_week:.0f}")

with col2:
    st.metric("_Unit Responses per Day_", f"{avg_unit_per_day:.1f}")

with col3:
    st.metric("_Unit Responses per Hour_", f"{avg_unit_per_hour:.1f}")

# Part c: Incident call type categories
st.subheader("Call Type Category by Incident and Unit Responses", divider = "green")
call_type_counts = incident_call_df['Call Type Category'].value_counts().reset_index()
call_type_counts.columns = ['Call Type Category', 'Count']
call_type_counts['Percentage'] = (call_type_counts['Count'] / call_type_counts['Count'].sum() * 100).round(2)
call_type_counts['Label'] = call_type_counts['Percentage'].apply(lambda x: f"{x:.2f}%")

unit_call_type_counts = unit_response_df['Call Type Category'].value_counts().reset_index()
unit_call_type_counts.columns = ['Call Type Category', 'Count']
unit_call_type_counts['Percentage'] = (unit_call_type_counts['Count'] / unit_call_type_counts['Count'].sum() * 100).round(2)
unit_call_type_counts['Label'] = unit_call_type_counts['Percentage'].apply(lambda x: f"{x:.2f}%")

fig1, fig2 = st.columns(2)
with fig1:
    st.subheader("Incident Calls by Call Type Category")
    chart1 = alt.Chart(call_type_counts.sort_values("Count", ascending=False)).mark_bar().encode(
        y=alt.Y('Call Type Category:N', sort=None, title="Call Type Category"),
        x=alt.X('Count:Q', title="Incident Calls"),
        color=alt.Color('Call Type Category:N', legend=None),
        tooltip=['Call Type Category', 'Count', 'Percentage']
    ).properties(
        width=350,
        height=350,
        title="Incident Calls by Call Type Category"
    )
    st.altair_chart(chart1, use_container_width=True)

with fig2:
    st.subheader("Unit Responses by Call Type Category")
    chart2 = alt.Chart(unit_call_type_counts.sort_values("Count", ascending=False)).mark_bar().encode(
        y=alt.Y('Call Type Category:N', sort=None, title="Call Type Category"),
        x=alt.X('Count:Q', title="Unit Responses"),
        color=alt.Color('Call Type Category:N', legend=None),
        tooltip=['Call Type Category', 'Count', 'Percentage']
    ).properties(
        width=350,
        height=350,
        title="Unit Responses by Call Type Category"
    )
    st.altair_chart(chart2, use_container_width=True)

# Top 20 active units by call type category
st.subheader("Top Active Units by Call Type Category", divider = "red")
unit_counts = unit_response_df.groupby(['Unit', 'Call Type Category']).size().reset_index(name='Count')
unit_totals = unit_counts.groupby('Unit')['Count'].sum().reset_index()
top_20_units = unit_totals.nlargest(20, 'Count')['Unit']
top_units_data = unit_counts[unit_counts['Unit'].isin(top_20_units)]
top_units_data = top_units_data.merge(unit_totals, on='Unit', suffixes=('', '_total'))

# Sort in descending order by total count
top_units_data = top_units_data.sort_values('Count_total', ascending=False)

fig3 = px.bar(
    top_units_data,
    x='Unit',
    y='Count',
    color='Call Type Category',
    hover_data=['Count', 'Call Type Category'],
    height=700  # Make the chart bigger
)
fig3.update_layout(
    xaxis={'tickangle': 45},
    yaxis_title="Number of Responses",
    showlegend=True
)
st.plotly_chart(fig3, use_container_width=True)

# Part e: Interactive map using Vega-Altair

st.header("Incident Locations Map ")

# Prepare the map dataframe
map_df = incident_call_df.dropna(subset=['Latitude', 'Longitude'])
map_df = map_df[(map_df['Latitude'] != 0) & (map_df['Longitude'] != 0)]

# Add a simple basemap using OpenStreetMap tiles via an image layer (no API required)
# Define the bounding box for Prince George's County (adjust as needed)
min_lon, max_lon = map_df['Longitude'].min(), map_df['Longitude'].max()
min_lat, max_lat = map_df['Latitude'].min(), map_df['Latitude'].max()

background = alt.Chart(pd.DataFrame({
    'url': ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
    'xmin': [min_lon],
    'xmax': [max_lon],
    'ymin': [min_lat],
    'ymax': [max_lat]
})).mark_image(
    width=800,
    height=500
).encode(
    x='xmin:Q',
    x2='xmax:Q',
    y='ymin:Q',
    y2='ymax:Q',
    url='url:N'
)

# Altair scatter plot for incident locations
points = alt.Chart(map_df).mark_circle(size=60).encode(
    longitude='Longitude:Q',
    latitude='Latitude:Q',
    color=alt.Color('Call Type Category:N', legend=alt.Legend(title="Call Type")),
    tooltip=[
        alt.Tooltip('Incident #:N', title='Incident #'),
        alt.Tooltip('City:N', title='City'),
        alt.Tooltip('Call Type Category:N', title='Call Type')
    ]
)

map_chart = background + points
map_chart = map_chart.properties(
    width=800,
    height=500,
    title="Incident Locations"
).interactive()

st.altair_chart(map_chart, use_container_width=True)

# Part g: Incident call response time table by station, call type category, and incident call type final
st.header("Incident Response Time Analysis by Station, Call Type, and Incident Type")

# Use the 'Response Time' column directly from the main data (already loaded as string HH:MM:SS)
def response_time_to_seconds(rt):
    if pd.isna(rt) or rt == "":
        return 0
    try:
        t = pd.to_datetime(rt, format="%H:%M:%S", errors="coerce")
        if pd.isnull(t):
            return 0
        return t.hour * 3600 + t.minute * 60 + t.second
    except Exception:
        return 0

def format_seconds_to_mmss(seconds):
    if pd.isna(seconds) or seconds <= 0:
        return ""
    minutes = int(seconds // 60)
    sec = int(seconds % 60)
    return f"{minutes:02d}:{sec:02d}"

# Prepare DataFrame for analysis
incident_call_df['Response Time (sec)'] = incident_call_df['Response Time'].apply(response_time_to_seconds)

# Mapping mutual aid stations (if needed, otherwise just use First Due Area)
mutual_aid_map = {}
incident_call_df['Station Name'] = incident_call_df['First Due Area'].map(mutual_aid_map).fillna(
    incident_call_df['First Due Area'])

# Filtering out non-numerical stations that aren't mutual aid
incident_response_times = incident_call_df[
    incident_call_df['Station Name'].fillna('').str.match(r'^\d+$|Mutual Aids|^$')
]

# Calculating average and 90th percentile response times (in seconds, then format to mm:ss)
incident_response_stats = incident_response_times.groupby(
    ['Station Name', 'Call Type Category', 'Incident Call Type Final']
)['Response Time (sec)'].agg([
    ('Average Response Time', lambda x: format_seconds_to_mmss(x[x > 0].mean()) if len(x[x > 0]) > 0 else ""),
    ('90th Percentile Response Time', lambda x: format_seconds_to_mmss(np.percentile(x[x > 0], 90) if len(x[x > 0]) > 0 else 0))
]).reset_index()

# Sorting by station name (numerical order for numbers, then mutual aids)
incident_response_stats['Sort Key'] = incident_response_stats['Station Name'].apply(
    lambda x: int(x) if str(x).isdigit() else float('inf'))
incident_response_stats = incident_response_stats.sort_values(
    ['Sort Key', 'Call Type Category', 'Incident Call Type Final']
).drop('Sort Key', axis=1)

st.write(incident_response_stats)

# Part h: Unit response time table by station, call type category, and incident call type final
st.header("Unit Response Time Analysis by Station, Call Type, and Incident Type")

# Use the 'Response Time' column directly from the main data for unit responses
unit_response_df['Response Time (sec)'] = unit_response_df['Response Time'].apply(response_time_to_seconds)

# Mapping mutual aid stations
mutual_aid_map = {}
unit_response_df['Station Name'] = unit_response_df['First Due Area'].map(mutual_aid_map).fillna(
    unit_response_df['First Due Area'])

# Filtering out non-numerical stations that aren't mutual aid
unit_response_times = unit_response_df[
    unit_response_df['Station Name'].fillna('').str.match(r'^\d+$|Mutual Aids|^$')
]

# Calculating average and 90th percentile response times (in seconds, then format to mm:ss)
unit_response_stats = unit_response_times.groupby(
    ['Station Name', 'Call Type Category', 'Incident Call Type Final']
)['Response Time (sec)'].agg([
    ('Average Response Time', lambda x: format_seconds_to_mmss(x[x > 0].mean()) if len(x[x > 0]) > 0 else ""),
    ('90th Percentile Response Time', lambda x: format_seconds_to_mmss(np.percentile(x[x > 0], 90) if len(x[x > 0]) > 0 else 0))
]).reset_index()

# Sorting by station name (numerical order for numbers, then mutual aids)
unit_response_stats['Sort Key'] = unit_response_stats['Station Name'].apply(
    lambda x: int(x) if str(x).isdigit() else float('inf'))
unit_response_stats = unit_response_stats.sort_values(
    ['Sort Key', 'Call Type Category', 'Incident Call Type Final']
).drop('Sort Key', axis=1)

st.write(unit_response_stats)

# Part h: Unit response time table by station, call type category, and incident call type final
st.header("Unit Response Time Analysis by Station, Call Type, and Incident Type")
# Calculating response time for unit responses (1st Unit Arrived - Dispatched)
unit_response_df['Response Time'] = (
    unit_response_df['1st Unit Arrived'] - unit_response_df['Dispatched']
).apply(lambda x: x if pd.notna(x) else pd.Timedelta(0))

def format_timedelta(td):
    # Accepts pd.Timedelta, np.timedelta64, or float/int seconds
    if pd.isna(td):
        return ""
    # Convert np.timedelta64 to pd.Timedelta
    if isinstance(td, np.timedelta64):
        td = pd.to_timedelta(td)
    # If it's a number (seconds), convert to Timedelta
    if isinstance(td, (int, float)):
        if td <= 0:
            return ""
        td = pd.to_timedelta(td, unit='s')
    # If it's not a Timedelta now, return blank
    if not isinstance(td, pd.Timedelta) or td <= pd.Timedelta(0):
        return ""
    total_seconds = td.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

unit_response_df['Response Time Str'] = unit_response_df['Response Time'].apply(format_timedelta)
# Converting to minutes and seconds
unit_response_df['Response Time Str'] = unit_response_df['Response Time'].apply(format_timedelta)
def format_timedelta(td):
    if pd.isna(td) or not isinstance(td, pd.Timedelta) or td <= pd.Timedelta(0):
        return ""
    total_seconds = td.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

unit_response_df['Response Time Str'] = unit_response_df['Response Time'].apply(format_timedelta)

# Mapping mutual aid stations
mutual_aid_map = {}
unit_response_df['Station Name'] = unit_response_df['First Due Area'].map(mutual_aid_map).fillna(
    unit_response_df['First Due Area'])

# Filtering out non-numerical stations that aren't mutual aid
unit_response_times = unit_response_df[
    unit_response_df['Station Name'].fillna('').str.match(r'^\d+$|Mutual Aids|^$')
]
# Calculating average and 90th percentile response times
unit_response_stats = unit_response_times.groupby(['Station Name', 'Call Type Category', 'Incident Call Type Final']).agg({
    'Response Time': [
        lambda x: format_timedelta(x.mean()),  # Average
        lambda x: format_timedelta(np.percentile(x[x != pd.Timedelta(0)], 90) if len(x[x != pd.Timedelta(0)]) > 0 else pd.Timedelta(0))  # 90th percentile
    ]
}).reset_index()
unit_response_stats.columns = ['Station Name', 'Call Type Category', 'Incident Call Type Final', 
                              'Average Response Time', '90th Percentile Response Time']

# Sorting by station name (numerical order for numbers, then mutual aids)
unit_response_stats['Sort Key'] = unit_response_stats['Station Name'].apply(
    lambda x: int(x) if x.isdigit() else float('inf'))
unit_response_stats = unit_response_stats.sort_values(['Sort Key', 'Call Type Category', 'Incident Call Type Final']).drop('Sort Key', axis=1)

st.write(unit_response_stats)

# a. Heatmap: Hour of Day vs Day of Week, populated with total_incidents
st.subheader("Incident Volume by Hour of Day and Day of Week")

# Ensure columns exist and are in correct format
incident_call_df['Date/Time Created'] = pd.to_datetime(incident_call_df['Date/Time Created'], errors='coerce')
incident_call_df['Hour of Day'] = incident_call_df['Date/Time Created'].dt.hour
incident_call_df['Day of Week'] = incident_call_df['Date/Time Created'].dt.day_name()

hour_day_counts = incident_call_df.groupby(['Day of Week', 'Hour of Day']).size().reset_index(name='Total Incidents')

# Order days for better display
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
hour_day_counts['Day of Week'] = pd.Categorical(hour_day_counts['Day of Week'], categories=days_order, ordered=True)

heatmap = alt.Chart(hour_day_counts).mark_rect().encode(
    x=alt.X('Hour of Day:O', title='Hour of Day'),
    y=alt.Y('Day of Week:N', sort=days_order, title='Day of Week'),
    color=alt.Color('Total Incidents:Q', scale=alt.Scale(scheme='reds')),
    tooltip=['Day of Week', 'Hour of Day', 'Total Incidents']
).properties(
    width=600,
    height=300,
    title="Incidents by Hour of Day and Day of Week"
)
st.altair_chart(heatmap, use_container_width=True)

# b. Pie chart: total_incidents per 'Call Type Category'
st.subheader("Incident Distribution by Call Type Category")

call_type_counts = incident_call_df['Call Type Category'].value_counts().reset_index()
call_type_counts.columns = ['Call Type Category', 'Total Incidents']

pie_chart = px.pie(
    call_type_counts,
    names='Call Type Category',
    values='Total Incidents',
    hole=0.3
)
st.plotly_chart(pie_chart, use_container_width=True)
