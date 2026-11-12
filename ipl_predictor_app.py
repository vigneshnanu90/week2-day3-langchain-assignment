import os
from typing import List, cast
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# Load OPENAI_API_KEY and LANGSMITH_* variables silently from local .env in the backend
load_dotenv(override=True)

# ---------------------------------------------------------------------------
# 1. PAGE CONFIG & BROADCAST STADIUM THEME (NO SIDEBAR)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="IPL Auction & Championship War Room",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* Hide sidebar toggle & default Streamlit chrome for a pure web-app feel */
    [data-testid="collapsedControl"], section[data-testid="stSidebar"] {
        display: none !important;
    }
    .stApp {
        background: radial-gradient(circle at top right, #0f291e 0%, #071318 45%, #040911 100%);
        color: #f8fafc;
    }
    /* Broadcast Header */
    .stadium-header {
        background: linear-gradient(120deg, #0b1f3a 0%, #102a43 55%, #1c3d2e 100%);
        border: 1px solid rgba(250, 204, 21, 0.45);
        border-left: 6px solid #facc15;
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 18px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .stadium-title {
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: 0.6px;
        background: linear-gradient(90deg, #fde047, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .stadium-sub {
        color: #cbd5e1;
        font-size: 1.02rem;
        margin-top: 6px;
    }
    /* Control Deck Container */
    .control-deck {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 14px;
        padding: 16px 20px 6px 20px;
        margin-bottom: 20px;
    }
    /* Podium Cards */
    .podium-gold {
        background: linear-gradient(145deg, rgba(161, 98, 7, 0.35), rgba(15, 23, 42, 0.9));
        border: 1.5px solid #facc15;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
    }
    .podium-silver {
        background: linear-gradient(145deg, rgba(51, 65, 85, 0.45), rgba(15, 23, 42, 0.9));
        border: 1.5px solid #94a3b8;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
    }
    .podium-emerald {
        background: linear-gradient(145deg, rgba(6, 95, 70, 0.4), rgba(15, 23, 42, 0.9));
        border: 1.5px solid #34d399;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
    }
    /* Trophy Cards */
    .franchise-card {
        background: rgba(15, 23, 42, 0.78);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
        transition: transform 0.2s ease;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 2. FRANCHISE TROPHY CABINET & METADATA (2008 - 2026)
# ---------------------------------------------------------------------------
FRANCHISE_DATA = [
    {"Code": "CSK", "Team": "Chennai Super Kings", "Titles": 5, "Years": "2010, 2011, 2018, 2021, 2023", "Home": "M. A. Chidambaram Stadium, Chennai", "Color": "#FACC15"},
    {"Code": "MI", "Team": "Mumbai Indians", "Titles": 5, "Years": "2013, 2015, 2017, 2019, 2020", "Home": "Wankhede Stadium, Mumbai", "Color": "#38BDF8"},
    {"Code": "KKR", "Team": "Kolkata Knight Riders", "Titles": 3, "Years": "2012, 2014, 2024", "Home": "Eden Gardens, Kolkata", "Color": "#C084FC"},
    {"Code": "RCB", "Team": "Royal Challengers Bengaluru", "Titles": 2, "Years": "2025, 2026", "Home": "M. Chinnaswamy Stadium, Bengaluru", "Color": "#F87171"},
    {"Code": "RR", "Team": "Rajasthan Royals", "Titles": 1, "Years": "2008", "Home": "Sawai Mansingh Stadium, Jaipur", "Color": "#F472B6"},
    {"Code": "SRH", "Team": "Sunrisers Hyderabad", "Titles": 1, "Years": "2016", "Home": "Rajiv Gandhi Intl. Stadium, Hyderabad", "Color": "#FB923C"},
    {"Code": "GT", "Team": "Gujarat Titans", "Titles": 1, "Years": "2022", "Home": "Narendra Modi Stadium, Ahmedabad", "Color": "#22D3EE"},
    {"Code": "DC", "Team": "Delhi Capitals", "Titles": 0, "Years": "Finalist (2020)", "Home": "Arun Jaitley Stadium, Delhi", "Color": "#60A5FA"},
    {"Code": "PBKS", "Team": "Punjab Kings", "Titles": 0, "Years": "Finalist (2014, 2025)", "Home": "Maharaja Yadavindra Singh Stadium, Mullanpur", "Color": "#EF4444"},
    {"Code": "LSG", "Team": "Lucknow Super Giants", "Titles": 0, "Years": "Playoffs (2022, 2023)", "Home": "BRSABV Ekana Cricket Stadium, Lucknow", "Color": "#2DD4BF"},
]

# ---------------------------------------------------------------------------
# 3. STRUCTURED OUTPUT SCHEMAS
# ---------------------------------------------------------------------------
class TeamStandingPrediction(BaseModel):
    rank: int = Field(description="Predicted rank from 1 to 10")
    team_name: str = Field(description="Full IPL franchise name")
    matches: int = Field(default=14, description="Total league matches played (14)")
    predicted_wins: int = Field(description="Predicted wins out of 14")
    predicted_losses: int = Field(description="Predicted losses out of 14")
    predicted_points: int = Field(description="Total league points (2 per win)")
    win_probability_pct: float = Field(description="Championship win probability percentage (0-100)")
    form_factor: str = Field(description="Concise 1-line tactical note based on historical records")


class SeasonForecast(BaseModel):
    target_year: int
    predicted_champion: str
    predicted_runner_up: str
    dark_horse_team: str
    championship_reasoning: str
    points_table: List[TeamStandingPrediction]


class MatchPrediction(BaseModel):
    winner: str
    win_probability: int = Field(description="Winner probability percentage between 50 and 99")
    predicted_margin: str
    pitch_and_tactical_edge: str


# ---------------------------------------------------------------------------
# 4. BACKEND SEARCH & MODEL HELPERS
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ipl_season_records(years: List[int]) -> str:
    """Fetches IPL points table and playoff records for each chosen season."""
    search_tool = DuckDuckGoSearchRun()
    collected_records = []
    for yr in years:
        query = f"IPL {yr} points table standings final winner runner up net run rate"
        try:
            snippet = search_tool.invoke(query)
        except Exception as exc:
            snippet = f"Record lookup note for {yr}: {exc}"
        collected_records.append(f"=== IPL {yr} SEASON RECORD ===\n{snippet}\n")
    return "\n".join(collected_records)


def get_llm(model_name: str = "gpt-4o-mini") -> ChatOpenAI:
    backend_key = os.getenv("OPENAI_API_KEY", "")
    if not backend_key:
        raise ValueError("OPENAI_API_KEY was not found in your backend environment or .env file.")
    return ChatOpenAI(model=model_name, temperature=0.3, api_key=SecretStr(backend_key))


# ---------------------------------------------------------------------------
# 5. TOP BROADCAST HEADER & INLINE MATCH CONTROL DECK
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="stadium-header">
        <div>
            <div class="stadium-title">🏏 TATA IPL CHAMPIONSHIP &amp; STANDINGS PREDICTOR</div>
            <div class="stadium-sub">
                Multi-Season Form Analytics • Playoff Qualification Projections • Franchise Legacy Vault
            </div>
        </div>
        <img src="https://upload.wikimedia.org/wikipedia/en/8/84/Indian_Premier_League_Official_Logo.svg" width="115" />
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="control-deck">', unsafe_allow_html=True)
ctrl1, ctrl2, ctrl3 = st.columns([1.2, 2.2, 1.3], vertical_alignment="center")

with ctrl1:
    target_year = st.selectbox("🎯 Target Season", options=[2027, 2028, 2029], index=0)

with ctrl2:
    lookback_years = st.slider(
        "📅 Historical Seasons Lookback Window",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of past IPL seasons analyzed to project upcoming standings",
    )

latest_completed = min(target_year - 1, 2026)
selected_years = list(range(latest_completed - lookback_years + 1, latest_completed + 1))

with ctrl3:
    st.markdown(f"**Active Form Window:**<br>`{selected_years[0]}` ➔ `{selected_years[-1]}` ({lookback_years} yrs)", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 6. MAIN NAVIGATION TABS
# ---------------------------------------------------------------------------
tab_predict, tab_h2h, tab_trophies = st.tabs(
    [
        f"🏆 {target_year} Points Table & Champion Forecast",
        "⚔️ Head-to-Head Match Center",
        "🏛️ Franchise Trophy Cabinet",
    ]
)

# ---------------------------------------------------------------------------
# TAB 1: SEASON & POINTS TABLE PREDICTOR
# ---------------------------------------------------------------------------
with tab_predict:
    head_l, head_r = st.columns([3.2, 1], vertical_alignment="center")
    with head_l:
        st.subheader(f"IPL {target_year} Projected Standings ({selected_years[0]}–{selected_years[-1]} Form Cycle)")
        st.caption("Top 4 franchises qualify for the IPL Playoffs (Qualifier 1, Eliminator, Qualifier 2 & Final).")
    with head_r:
        run_forecast = st.button(f"🏏 Generate {target_year} Forecast", type="primary", use_container_width=True)

    if run_forecast:
        try:
            with st.status(f"Gathering {selected_years[0]}–{selected_years[-1]} IPL season records & simulating {target_year}...", expanded=True) as status:
                web_history = fetch_ipl_season_records(selected_years)
                status.update(label="Calculating Net Run Rate momentum & playoff probabilities...", state="running")

                llm = get_llm().with_structured_output(SeasonForecast)
                prompt = f"""
                You are an elite IPL cricket statistician and tournament analyst.
                Analyze the historical IPL season records below covering {selected_years}:

                {web_history}

                Based strictly on multi-year consistency, recent momentum, Net Run Rate trends, and playoff conversion
                across these {lookback_years} seasons, predict the complete IPL {target_year} tournament outcome:
                1. Predict the IPL {target_year} Champion, Runner-Up, and Dark Horse.
                2. Generate a realistic 10-team league points table (14 matches per team, 2 points per win) ranked 1 to 10.
                3. Ensure championship win probabilities across all 10 teams sum reasonably to ~100%.
                """
                forecast = cast(SeasonForecast, llm.invoke(prompt))
                st.session_state["forecast"] = forecast
                st.session_state["web_history"] = web_history
                status.update(label=f"IPL {target_year} Forecast Ready!", state="complete", expanded=False)
        except Exception as err:
            st.error(f"Backend Configuration Error: {err}")

    if "forecast" in st.session_state:
        fc: SeasonForecast = st.session_state["forecast"]

        # Podium Display
        p1, p2, p3 = st.columns(3)
        with p1:
            st.markdown(
                f"""<div class="podium-gold">
                    <div style="color:#facc15; font-weight:700; font-size:0.85rem;">🏆 PREDICTED {fc.target_year} CHAMPION</div>
                    <div style="font-size:1.55rem; font-weight:800; margin-top:6px;">{fc.predicted_champion}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with p2:
            st.markdown(
                f"""<div class="podium-silver">
                    <div style="color:#cbd5e1; font-weight:700; font-size:0.85rem;">🥈 PREDICTED RUNNER-UP</div>
                    <div style="font-size:1.55rem; font-weight:800; margin-top:6px;">{fc.predicted_runner_up}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with p3:
            st.markdown(
                f"""<div class="podium-emerald">
                    <div style="color:#34d399; font-weight:700; font-size:0.85rem;">⚡ TOURNAMENT DARK HORSE</div>
                    <div style="font-size:1.55rem; font-weight:800; margin-top:6px;">{fc.dark_horse_team}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("")
        st.info(f"**Chief Analyst Verdict:** {fc.championship_reasoning}")

        # Points Table with Playoff Qualification Tag
        st.subheader(f"📊 Projected IPL {fc.target_year} League Points Table")
        rows = []
        for row in sorted(fc.points_table, key=lambda r: r.rank):
            status_badge = "🟢 Playoff Q" if row.rank <= 4 else "⚪ League"
            rows.append(
                {
                    "Pos": row.rank,
                    "Status": status_badge,
                    "Franchise": row.team_name,
                    "M": row.matches,
                    "W": row.predicted_wins,
                    "L": row.predicted_losses,
                    "Pts": row.predicted_points,
                    "Title Win %": row.win_probability_pct,
                    "Tactical Edge": row.form_factor,
                }
            )
        df_table = pd.DataFrame(rows)
        st.dataframe(
            df_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Title Win %": st.column_config.ProgressColumn(
                    "Title Win %", format="%.1f%%", min_value=0, max_value=40
                ),
            },
        )

        st.subheader("📈 Championship Win Probability Share")
        st.bar_chart(df_table.set_index("Franchise")[["Title Win %"]], color="#facc15")

        with st.expander("📂 View Historical Season Records Analyzed"):
            st.text(st.session_state.get("web_history", ""))

# ---------------------------------------------------------------------------
# TAB 2: HEAD-TO-HEAD MATCH CENTER
# ---------------------------------------------------------------------------
with tab_h2h:
    st.subheader("⚔️ Head-to-Head Matchup Simulator")
    team_names = [t["Team"] for t in FRANCHISE_DATA]

    col_t1, col_t2, col_venue = st.columns(3)
    with col_t1:
        team_a = st.selectbox("Home Franchise", team_names, index=0)
    with col_t2:
        team_b = st.selectbox("Away Franchise", team_names, index=3)
    with col_venue:
        venue = st.selectbox(
            "Stadium & Pitch Conditions",
            [
                "M. A. Chidambaram Stadium, Chennai (Spin & Grip)",
                "Wankhede Stadium, Mumbai (True Bounce & Dew)",
                "M. Chinnaswamy Stadium, Bengaluru (High-Scoring Flat Track)",
                "Narendra Modi Stadium, Ahmedabad (Balanced Pace & Spin)",
                "Eden Gardens, Kolkata (Fast Outfield & Evening Dew)",
            ],
        )

    if st.button("🏏 Simulate Match Result", type="primary"):
        if team_a == team_b:
            st.warning("Please choose two different franchises for a head-to-head fixture.")
        else:
            try:
                with st.spinner(f"Simulating {team_a} vs {team_b} at {venue.split(' (')[0]}..."):
                    web_history = fetch_ipl_season_records(selected_years)
                    h2h_llm = get_llm().with_structured_output(MatchPrediction)
                    h2h_prompt = f"""
                    Using the multi-year IPL historical records ({selected_years}) below:
                    {web_history}

                    Simulate an IPL {target_year} match between {team_a} and {team_b} at {venue}.
                    Predict the match winner, win probability percentage, victory margin, and tactical/pitch edge.
                    """
                    match_res = cast(MatchPrediction, h2h_llm.invoke(h2h_prompt))

                    st.success(f"### 🏆 Projected Winner: **{match_res.winner}** ({match_res.win_probability}% Win Probability)")
                    st.write(f"**Estimated Margin:** {match_res.predicted_margin}")
                    st.write(f"**Pitch & Tactical Breakdown:** {match_res.pitch_and_tactical_edge}")
            except Exception as err:
                st.error(f"Backend Configuration Error: {err}")

# ---------------------------------------------------------------------------
# TAB 3: FRANCHISE TROPHY CABINET
# ---------------------------------------------------------------------------
with tab_trophies:
    st.subheader("🏛️ IPL All-Time Franchise Trophy Cabinet (2008 – 2026)")

    trophy_df = pd.DataFrame(FRANCHISE_DATA)
    st.bar_chart(trophy_df.set_index("Team")["Titles"], color="#34d399")

    cols = st.columns(2)
    for idx, team in enumerate(FRANCHISE_DATA):
        trophy_icons = "🏆 " * team["Titles"] if team["Titles"] > 0 else "🎯 Chasing Maiden Title"
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div class="franchise-card" style="border-left: 5px solid {team['Color']};">
                    <h4 style="margin:0; color:{team['Color']};">{team['Team']} ({team['Code']})</h4>
                    <p style="margin:6px 0; font-size:1.05rem;"><strong>Championships ({team['Titles']}):</strong> {trophy_icons}</p>
                    <p style="margin:2px 0; color:#e2e8f0;"><strong>Title / Best Seasons:</strong> {team['Years']}</p>
                    <p style="margin:2px 0; color:#94a3b8;"><strong>Home Ground:</strong> {team['Home']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )