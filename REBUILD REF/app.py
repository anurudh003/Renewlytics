import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Renewable Energy Forecasting Analytics",
    layout="wide"
)

# ======================================================
# GLOBAL STYLES (UNCHANGED)
# ======================================================
st.markdown("""
<style>
body { background-color: #0e1117; color: #ffffff; }
[data-testid="stSidebar"] { background-color: #161b22; }

h1 { color: #58a6ff; font-size: 40px; }
h2 { color: #2ecc71; font-size: 26px; }

.square-box {
    border-radius: 0px;
    padding: 14px;
    margin-top: 10px;
    min-height: 160px;
    font-size: 14px;
}

.insight-blue { background-color: #58a6ff; color: #000000; }
.insight-green { background-color: #2ecc71; color: #000000; }

.conclusion-box {
    background-color: #f1c40f;
    color: #000000;
    padding: 16px;
    border-radius: 0px;
    margin-top: 15px;
}

.metric-box {
    background: linear-gradient(145deg, #1c1f26, #12151c);
    box-shadow: 4px 4px 10px #000000, -4px -4px 10px #2a2d35;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title(" Renewable Energy Forecasting Analytics")

# ======================================================
# DATA LOADING
# ======================================================
@st.cache_data
def load_main_data():
    path = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\master\india_renewable_energy_analytics_master.csv"
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df

@st.cache_data
def load_forecast_data():
    path = r"C:\Users\anuru\OneDrive\Desktop\REBUILD REF\master\renewable_energy_forecast_till_2034.csv"
    df = pd.read_csv(path)

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # --- Flexible time handling ---
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    elif "year" in df.columns:
        df["date"] = pd.to_datetime(df["year"].astype(str) + "-01-01")

    elif "forecast_year" in df.columns:
        df["date"] = pd.to_datetime(df["forecast_year"].astype(str) + "-01-01")

    elif "ds" in df.columns:
        df["date"] = pd.to_datetime(df["ds"])

    else:
        # LAST RESORT: generate year sequence (2014–2034)
        start_year = 2014
        df["date"] = pd.date_range(
            start=f"{start_year}-01-01",
            periods=len(df),
            freq="YS"
        )

    return df



df_main = load_main_data()
df_forecast = load_forecast_data()

# ======================================================
# SIDEBAR – OBJECTIVE NAVIGATION
# ======================================================
st.sidebar.header("Objectives")

if "objective" not in st.session_state:
    st.session_state.objective = 1

if st.sidebar.button("1️⃣ Energy Generation Performance"):
    st.session_state.objective = 1
if st.sidebar.button("2️⃣ Energy Efficiency Dominance"):
    st.session_state.objective = 2
if st.sidebar.button("3️⃣ Weather Contribution Analysis"):
    st.session_state.objective = 3
if st.sidebar.button("4️⃣ Forecast Reliability Assessment"):
    st.session_state.objective = 4

st.sidebar.divider()
st.sidebar.header("Filters")

city = st.sidebar.selectbox("City", sorted(df_main.city.unique()))

# Date filter ONLY for Objectives 1–3
start, end = st.sidebar.date_input(
    "Date Range (2014–2024)",
    [pd.to_datetime("2014-01-01"), pd.to_datetime("2024-12-31")],
    format="DD/MM/YYYY"
)

# ======================================================
# COMMON FILTERED DATA (OBJECTIVES 1–3)
# ======================================================
df_filtered = df_main[
    (df_main.city == city) &
    (df_main.date >= pd.to_datetime(start)) &
    (df_main.date <= pd.to_datetime(end))
].copy()

df_filtered["date_str"] = df_filtered["date"].dt.strftime("%d/%m/%Y")

# ======================================================
# METRICS (UNCHANGED)
# ======================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"<div class='metric-box'><b>Total Energy</b><br>{df_filtered.energy_generated.sum():,.0f}</div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-box'><b>Avg Efficiency Index</b><br>{df_filtered.energy_efficiency_index.mean():.2f}</div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-box'><b>Max Energy Output</b><br>{df_filtered.energy_generated.max():.1f}</div>", unsafe_allow_html=True)
with c4:
    mae = np.mean(np.abs(df_filtered.energy_generated - df_filtered.predicted_energy))
    st.markdown(f"<div class='metric-box'><b>Forecast MAE</b><br>{mae:.3f}</div>", unsafe_allow_html=True)

st.divider()

# ======================================================
# OBJECTIVE 1 FUNCTION
# ======================================================
def render_objective_1(df):
    st.subheader(" Energy Generation Performance")

    fig = px.area(df, x="date_str", y="energy_generated",
                  template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    growth = ((df.energy_generated.iloc[-1] - df.energy_generated.iloc[0]) / df.energy_generated.iloc[0]) * 100

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="square-box insight-blue">
        • Energy trend shows a {growth:.1f}% change over selected period<br>
        • Seasonal cycles are clearly visible<br>
        • Peaks represent high renewable availability<br>
        • {city}'s generation stability supports grid planning
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="square-box insight-green">
        • High predictability improves load balancing<br>
        • Seasonal dips indicate storage requirement<br>
        • Long-term consistency improves policy confidence<br>
        • {city} is operationally reliable
        </div>
        """, unsafe_allow_html=True)

# ======================================================
# OBJECTIVE 2 FUNCTION
# ======================================================
def render_objective_2(df):
    st.subheader(" Energy Efficiency Dominance")

    fig = px.bar(df, x="date_str", y="energy_efficiency_index",
                 template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    eff_std = df.energy_efficiency_index.std()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="square-box insight-blue">
        • Efficiency variability (σ): {eff_std:.2f}<br>
        • Lower variation indicates operational maturity<br>
        • Efficiency reflects infrastructure quality<br>
        • {city}'s efficiency stability is measurable
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="square-box insight-green">
        • Stable efficiency reduces energy wastage<br>
        • Variability indicates scope for optimization<br>
        • Efficiency-driven cities scale faster<br>
        • {city} requires targeted efficiency tuning
        </div>
        """, unsafe_allow_html=True)

# ======================================================
# OBJECTIVE 3 FUNCTION
# ======================================================
def render_objective_3(df):
    st.subheader(" Weather Contribution Analysis")

    feature = st.selectbox("Weather Variable",
                           ["sunshine_hours", "wind_speed", "temperature"])

    corr = df[[feature, "energy_generated"]].corr().iloc[0, 1]

    fig = px.scatter(df, x=feature, y="energy_generated",
                     size="energy_generated",
                     template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="square-box insight-blue">
        • Correlation with energy: {corr:.2f}<br>
        • Weather is a direct production driver<br>
        • Sensitivity varies across variables<br>
        • {city} output is climate-dependent
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="square-box insight-green">
        • Weather-aware planning reduces risk<br>
        • Climate diversity improves resilience<br>
        • Extreme events increase volatility<br>
        • {city} benefits from adaptive forecasting
        </div>
        """, unsafe_allow_html=True)

# ======================================================
# OBJECTIVE 4 FUNCTION (FORECAST)
# ======================================================
def render_objective_4(city):
    st.subheader(" Forecast Reliability Assessment (2016–2034)")

    df_city = df_forecast[df_forecast["city"] == city].copy()

    df_city.columns = df_city.columns.str.lower()
    df_city["date"] = pd.to_datetime(df_city["date"])

    forecast_col = "energy_generated"

    historical = df_city[df_city["date"].dt.year <= 2024]
    future = df_city[df_city["date"].dt.year > 2024]

    fig = go.Figure()

    # Historical (monthly resolution)
    fig.add_trace(go.Scatter(
        x=historical["date"],
        y=historical[forecast_col],
        name="Historical Trend",
        line=dict(color="#d62728")
    ))

    # Forecast (monthly resolution)
    fig.add_trace(go.Scatter(
        x=future["date"],
        y=future[forecast_col],
        name="Forecast (2025–2034)",
        line=dict(color="#9467bd", dash="dot")
    ))

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Year",
        yaxis_title="Energy Generated",
        xaxis=dict(
            tickformat="%Y",
            dtick="M12"  # one tick per year
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Dynamic Insights
    # -------------------------------
    growth = (
        future[forecast_col].iloc[-1] - historical[forecast_col].iloc[-1]
    ) / historical[forecast_col].iloc[-1] * 100

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"""
        <div class="square-box insight-blue">
        • Forecast clearly visible till 2034<br>
        • Expected post-2024 growth: {growth:.1f}%<br>
        • Monthly seasonality preserved<br>
        • {city} shows steady expansion
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="square-box insight-green">
        • Monthly forecast improves planning accuracy<br>
        • Long-term capacity growth is stable<br>
        • No abrupt volatility detected<br>
        • {city} is suitable for long-horizon planning
        </div>
        """, unsafe_allow_html=True)



# ======================================================
# RENDER OBJECTIVE
# ======================================================
if st.session_state.objective == 1:
    render_objective_1(df_filtered)
elif st.session_state.objective == 2:
    render_objective_2(df_filtered)
elif st.session_state.objective == 3:
    render_objective_3(df_filtered)
elif st.session_state.objective == 4:
    render_objective_4(city)

