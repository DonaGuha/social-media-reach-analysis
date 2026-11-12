import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="Social Media Reach Analysis",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Social Media Reach Analysis Dashboard")
st.markdown(
    "Analyze social media performance, audience engagement "
    "and reach across different platforms."
)

# Load Dataset
@st.cache_data
def load_data():
    return pd.read_csv("social_media_data.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("Dataset not found. Please add social_media_data.csv.")
    st.stop()

# Data Cleaning
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

numeric_columns = [
    "Impressions", "Reach", "Likes", "Comments",
    "Shares", "Saves", "Followers_Gained", "Link_Clicks"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df = df.dropna(subset=["Date"])

# Calculate Engagement
df["Engagement"] = (
    df["Likes"] +
    df["Comments"] +
    df["Shares"] +
    df["Saves"]
)

df["Engagement_Rate"] = (
    df["Engagement"] / df["Reach"].replace(0, pd.NA)
) * 100

df["Engagement_Rate"] = df["Engagement_Rate"].fillna(0)

# Sidebar Filters
st.sidebar.header("🔍 Dashboard Filters")

platforms = ["All"] + sorted(df["Platform"].unique().tolist())

selected_platform = st.sidebar.selectbox(
    "Select Platform",
    platforms
)

post_types = ["All"] + sorted(df["Post_Type"].unique().tolist())

selected_post = st.sidebar.selectbox(
    "Select Post Type",
    post_types
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply Filters
filtered_df = df.copy()

if selected_platform != "All":
    filtered_df = filtered_df[
        filtered_df["Platform"] == selected_platform
    ]

if selected_post != "All":
    filtered_df = filtered_df[
        filtered_df["Post_Type"] == selected_post
    ]

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date) &
        (filtered_df["Date"].dt.date <= end_date)
    ]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# KPI Metrics
st.subheader("📈 Key Performance Indicators")

total_impressions = int(filtered_df["Impressions"].sum())
total_reach = int(filtered_df["Reach"].sum())
total_engagement = int(filtered_df["Engagement"].sum())
total_followers = int(filtered_df["Followers_Gained"].sum())
total_clicks = int(filtered_df["Link_Clicks"].sum())

avg_engagement_rate = filtered_df["Engagement_Rate"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Impressions", f"{total_impressions:,}")
col2.metric("Total Reach", f"{total_reach:,}")
col3.metric("Total Engagement", f"{total_engagement:,}")
col4.metric("Avg. Engagement Rate", f"{avg_engagement_rate:.2f}%")

col5, col6 = st.columns(2)

col5.metric("Followers Gained", f"{total_followers:,}")
col6.metric("Total Link Clicks", f"{total_clicks:,}")

st.divider()

# Platform Analysis
st.subheader("📱 Platform Performance")

platform_data = filtered_df.groupby("Platform", as_index=False).agg({
    "Reach": "sum",
    "Impressions": "sum",
    "Engagement": "sum"
})

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        platform_data,
        x="Platform",
        y="Reach",
        color="Platform",
        title="Reach by Social Media Platform",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.pie(
        platform_data,
        names="Platform",
        values="Engagement",
        title="Engagement Distribution",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Daily Reach Analysis
st.subheader("📅 Reach and Impressions Over Time")

daily_data = filtered_df.groupby("Date", as_index=False).agg({
    "Reach": "sum",
    "Impressions": "sum"
})

fig = px.line(
    daily_data,
    x="Date",
    y=["Reach", "Impressions"],
    markers=True,
    title="Daily Social Media Performance"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# Post Type Analysis
st.subheader("📝 Post Type Performance")

post_data = filtered_df.groupby("Post_Type", as_index=False).agg({
    "Reach": "sum",
    "Engagement": "sum",
    "Likes": "sum",
    "Comments": "sum",
    "Shares": "sum"
})

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        post_data,
        x="Post_Type",
        y="Reach",
        color="Post_Type",
        title="Reach by Post Type"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        post_data,
        x="Post_Type",
        y="Engagement",
        color="Post_Type",
        title="Engagement by Post Type"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Engagement Analysis
st.subheader("❤️ Engagement Analysis")

engagement_data = filtered_df[
    ["Platform", "Likes", "Comments", "Shares", "Saves"]
].groupby("Platform", as_index=False).sum()

fig = px.bar(
    engagement_data,
    x="Platform",
    y=["Likes", "Comments", "Shares", "Saves"],
    barmode="group",
    title="Likes, Comments, Shares and Saves"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# Followers Analysis
st.subheader("👥 Audience Growth")

follower_data = filtered_df.groupby(
    "Platform", as_index=False
)["Followers_Gained"].sum()

fig = px.bar(
    follower_data,
    x="Platform",
    y="Followers_Gained",
    color="Platform",
    title="Followers Gained by Platform"
)

st.plotly_chart(fig, use_container_width=True)

# Data Table
st.subheader("📋 Social Media Dataset")

st.dataframe(
    filtered_df,
    use_container_width=True
)

# Download Filtered Data
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=csv,
    file_name="filtered_social_media_data.csv",
    mime="text/csv"
)

# Automatic Insights
st.divider()

st.subheader("💡 Key Insights")

best_platform = platform_data.loc[
    platform_data["Reach"].idxmax(), "Platform"
]

best_post = post_data.loc[
    post_data["Engagement"].idxmax(), "Post_Type"
]

st.success(
    f"🏆 {best_platform} generated the highest total reach."
)

st.info(
    f"📌 {best_post} generated the highest total engagement."
)

st.write(
    f"📊 The dataset contains {len(filtered_df)} social media posts."
)

st.write(
    f"❤️ Average engagement rate: {avg_engagement_rate:.2f}%"
)

st.caption("Social Media Reach Analysis | Data Analytics Internship Project")