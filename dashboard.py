import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px

day_df = pd.read_csv("day_final.csv")
hour_df = pd.read_csv("hour_final.csv")

st.set_page_config(layout="wide")

st.markdown(
    "<h1 style = 'text-align: center;'>BIKE SHARING ANALYTICS DASHBOARD</h1>",
    unsafe_allow_html = True
)

st.markdown(
    """<h6 style = 'text-align: center;'>This dashboard explores bike rental patterns based on time, weather, and user behavior using the Capital Bike Sharing dataset (2011–2012)</h6>""",
    unsafe_allow_html = True
)


##SIDEBAR
st.sidebar.markdown(
    "<h2 style = 'text-align: center;'>FILTERS</h2>",
    unsafe_allow_html = True
)

year_map = {0: 2011, 1: 2012}
day_df["year_label"] = day_df["yr"].map(year_map)
hour_df["year_label"] = hour_df["yr"].map(year_map)

selected_year = st.sidebar.multiselect(
    "Select Year",
    options = sorted(day_df["year_label"].unique()),
    default = sorted(day_df["year_label"].unique())
)

season_map = {1: "Springer", 2: "Summer", 3: "Fall", 4: "Winter"}
day_df["season_label"] = day_df["season"].map(season_map)
hour_df["season_label"] = hour_df["season"].map(season_map)
selected_season = st.sidebar.multiselect(
    "Select Season",
    options = sorted(day_df["season_label"].unique()),
    default = sorted(day_df["season_label"].unique())
)

weather_map = {1: "Clear", 2: "Misty", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}
day_df["weather_label"] = day_df["weathersit"].map(weather_map)
hour_df["weather_label"] = hour_df["weathersit"].map(weather_map)
selected_weather = st.sidebar.multiselect(
    "Select Weather",
    options = sorted(day_df["weather_label"].unique()),
    default = sorted(day_df["weather_label"].unique())
)

user_type = st.sidebar.radio(
    "User Type",
    options = ["Total", "Casual", "Registered"],
    index = 0
)

##FILTER
filtered_day = day_df[
    (day_df["year_label"].isin(selected_year)) &
    (day_df["season_label"].isin(selected_season)) &
    (day_df["weather_label"].isin(selected_weather))
]

filtered_hour = hour_df[
    (hour_df["year_label"].isin(selected_year)) &
    (hour_df["season_label"].isin(selected_season)) &
    (hour_df["weather_label"].isin(selected_weather))
]

filtered_day["dteday"] = pd.to_datetime(filtered_day["dteday"])

def get_target(df):
    if user_type == "Casual":
        return df["casual"]
    elif user_type == "Registered":
        return df["registered"]
    else:
        return df["cnt"]

#KPI
total_rental = int(get_target(filtered_day).sum())
avg_rental = int(get_target(filtered_day).mean())
def calculate_yoy(df):
    yearly = df.groupby("year_label")[get_target(df).name].sum()
    if 2011 in yearly.index and 2012 in yearly.index:
        yoy = ((yearly[2012] - yearly[2011])/yearly[2011]) * 100
        return round(yoy, 2)
    else:
        return None
yoy_growth = calculate_yoy(filtered_day)

col1, col2, col3 = st.columns(3)
col1.markdown(f"""
            <div style="text-align:center;">
                <h3>Total Rentals</h3>
                <h3>{total_rental:,}</h3>
            </div>
            """, unsafe_allow_html=True
)

col2.markdown(f"""
            <div style = 'text-align: center;'>
                <h3>Average Rental</h3>
                <h3>{avg_rental:,}</h3>
            </div>
            """, unsafe_allow_html = True
)

col3.markdown(f"""
            <div style = 'text-align: center;'>
                <h3>YoY Growth</h3>
                <h3>{yoy_growth:+.2f}%</h3>
            </div>
            """, unsafe_allow_html = True
)

tab_day, tab_hour = st.tabs(["Daily Analytics", "Hourly Analytics"])

with tab_day:
    st.markdown("<h2 style = 'text-align: center;'>Daily Rentals</h2>", unsafe_allow_html = True)

    peak_day = filtered_day.loc[get_target(filtered_day).idxmax(), "dteday"].date()
    lower_day = filtered_day.loc[get_target(filtered_day).idxmin(), "dteday"].date()

    col1, col2 = st.columns(2)
    col1.markdown(f"""
    <div style = "text-align: center;">
        <h4>Peak Day</h4>
        <h4>{peak_day.strftime("%d %b %Y")}</h4>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div style = "text-align: center;">
        <h4>Lowest Day</h4>
        <h4>{lower_day.strftime("%d %b %Y")}</h4>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Average Rentals Per Month")
    monthly_avg = filtered_day.groupby("mnth")[["cnt", "casual", "registered"]].mean().reset_index()
    fig = px.line(
        monthly_avg,
        x="mnth",
        y=get_target(monthly_avg).name,
        markers=True,
        labels = {"mnth": "Month", get_target(monthly_avg).name: "Average Rentals"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Average Rentals by Day Type")
    day_type = filtered_day.copy()
    day_type["day_type"] = np.where(
        day_type["holiday"] == 1, "Holiday",
        np.where(day_type["workingday"] == 1, "Working Day", "Weekday")
    )
    day_type_avg = day_type.groupby("day_type")[["cnt", "casual", "registered"]].mean().reset_index().sort_values(by=get_target(filtered_day).name, ascending=False)
    fig = px.bar(
        day_type_avg,
        x = "day_type",
        y = get_target(day_type_avg).name,
        labels = {"day_type": "Day Type", get_target(day_type_avg).name: "Average Rentals"},
    )
    st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Average Rentals by Season")
        season_avg = filtered_day.groupby("season_label")[["cnt", "casual", "registered"]].mean().reset_index().sort_values(by=get_target(filtered_day).name, ascending=False)

        fig = px.bar(
            season_avg,
            x = "season_label",
            y = get_target(season_avg).name,
            labels = {"season_label": "Season", get_target(season_avg).name: "Average Rentals"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Average Rentals by Weather")
        weather_avg = filtered_day.groupby("weather_label")[["cnt", "casual", "registered"]].mean().reset_index().sort_values(by=get_target(filtered_day).name, ascending=False)

        fig = px.bar(
            weather_avg,
            x = "weather_label",
            y = get_target(weather_avg).name,
            labels = {"weather_label": "Weather", get_target(weather_avg).name: "Average Rentals"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Windspeed vs Rentals")
    fig = px.scatter(
        filtered_day,
        x = "windspeed",
        y = get_target(filtered_day).name,
        trendline = "ols",
        labels = {"windspeed": "Windspeed", get_target(filtered_day).name: "Rentals"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Key Insights (Daily)")

    peak_month = monthly_avg.loc[monthly_avg[get_target(monthly_avg).name].idxmax(), "mnth"]
    peak_season = season_avg.loc[season_avg[get_target(season_avg).name].idxmax(), "season_label"]
    dominant_day_type = day_type_avg.loc[day_type_avg[get_target(day_type_avg).name].idxmax(), "day_type"]

    dominant_user = "Registered" if filtered_day["registered"].sum() > filtered_day["casual"].sum() else "Casual"

    corr_wind = filtered_day["windspeed"].corr(get_target(filtered_day))

    insight1 = f"The highest average rentals occur in month {int(peak_month)}, indicating strong seasonal demand."
    insight2 = f"{peak_season} shows the highest average bike rental activity among all seasons."
    insight3 = f"{dominant_day_type} records the highest average rentals compared to other day types."
    insight4 = f"{dominant_user} users dominate total bike rentals in the selected data."
    insight5 = (
        f"Windspeed has a weak negative correlation with rentals ({corr_wind:.2f}), "
        "suggesting that higher wind slightly reduces demand."
        if corr_wind < 0 else
        f"Windspeed shows little to no negative impact on bike rentals ({corr_wind:.2f})."
    )

    st.success(insight1)
    st.success(insight2)
    st.success(insight3)
    st.success(insight4)
    st.success(insight5)

    with st.expander("Show Raw Data"):
        st.dataframe(filtered_day)

with tab_hour:
    st.markdown("<h1 style = 'text-align: center;'>Hourly Rentals</h1>", unsafe_allow_html = True)

    peak_hour = filtered_hour.loc[get_target(filtered_hour).idxmax(), "hr"]
    lower_hour = filtered_hour.loc[get_target(filtered_hour).idxmin(), "hr"]

    col1, col2 = st.columns(2)

    col1.markdown(f"""
    <div style = "text-align: center;">
        <h4>Peak Day</h4>
        <h4>{peak_hour}:00</h4>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div style = "text-align: center;">
        <h4>Lowest Day</h4>
        <h4>{lower_hour}:00</h4>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Average Rentals per Hour")
    hourly_avg = filtered_hour.groupby("hr")[["cnt", "casual", "registered"]].mean().reset_index()
    fig = px.line(
        hourly_avg,
        x = "hr",
        y = get_target(hourly_avg).name,
        markers = True,
        labels = {"hr": "Hour", get_target(hourly_avg).name: "Average Rentals"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Rentals by Day Type per Hour")
    day_type_hour = filtered_hour.copy()
    day_type_hour["day_type_hour"] = np.where(
        day_type_hour["holiday"] == 1, "Holiday",
        np.where(day_type_hour["workingday"] == 1, "Working Day", "Weekday")
    )
    day_type_hour_avg = day_type_hour.groupby(["day_type_hour", "hr"])[["cnt", "casual", "registered"]].mean().reset_index()
    fig = px.line(
        day_type_hour_avg,
        x = "hr",
        y = get_target(day_type_hour_avg).name,
        color = "day_type_hour",
        markers = True,
        labels = {"hr": "Hour", get_target(day_type_hour_avg).name: "Average Rentals", "day_type_hour": "Day Type"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Rentals by Season per Hour")
    season_hour = filtered_hour.groupby(["season_label", "hr"])[["cnt", "casual", "registered"]].mean().reset_index()
    fig = px.line(
        season_hour,
        x = "hr",
        y = get_target(season_hour).name,
        color = "season_label",
        markers = True,
        labels = {"hr": "Hour", get_target(season_hour).name: "Average Rentals", "season_label": "Season"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Rentals by Weather per Hour")
    weather_hour = filtered_hour.groupby(["weather_label", "hr"])[["cnt", "casual", "registered"]].mean().reset_index()
    fig = px.line(
        weather_hour,
        x = "hr",
        y = get_target(weather_hour).name,
        color = "weather_label",
        markers = True,
        labels = {"hr": "Hour", get_target(weather_hour).name: "Average Rentals", "weather_label": "Weather"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Key Insights (Hourly)")

    dominant_season_hr = season_hour.groupby("season_label")[get_target(season_hour).name].mean().idxmax()
    dominant_weather_hr = weather_hour.groupby("weather_label")[get_target(weather_hour).name].mean().idxmax()

    insight1 = f"Peak rental activity occurs around {int(peak_hour)}:00, while the lowest demand is around {int(lower_hour)}:00."
    insight2 = f"{dominant_season_hr} records the highest hourly rental averages."
    insight3 = f"{dominant_weather_hr} weather conditions show the strongest hourly rental performance."
    insight4 = f"{user_type} users dominate rentals during peak hours in the selected filters."

    st.success(insight1)
    st.success(insight2)
    st.success(insight3)
    st.success(insight4)

    with st.expander("Show Raw Data"):
        st.dataframe(filtered_hour)
