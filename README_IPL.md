# TATA IPL Championship & Standings Predictor (`ipl_predictor_app.py`)

`ipl_predictor_app.py` is a full-screen Streamlit web application that dynamically fetches live historical IPL standings and playoff records from the web, analyzes multi-season team form, and projects upcoming season points tables and head-to-head match outcomes.

All API credentials and LangSmith tracing variables are loaded silently on the backend via `.env`—no keys are requested in the UI, and no tracing code is embedded in the application.

## Key Features

* **Dynamic Multi-Season Web Search:** Select any target season (`2027`–`2029`) and historical lookback window (`1` to `10` past seasons). Live season standings and Net Run Rate trends are gathered automatically from the web with zero extra search API keys required.
* **Projected 10-Team Points Table & Podium:** Generates predicted Champion, Runner-Up, Dark Horse, playoff qualification status (`Top 4`), projected wins/losses, points, and championship win probability percentages.
* **Head-to-Head Match Simulator:** Simulates matchups between any two IPL franchises across major Indian venues with pitch-specific tactical breakdowns.
* **Franchise Trophy Cabinet (2008–2026):** Interactive visual breakdown of all 10 franchises, championship titles, winning years, and home stadiums.

## 1. Install Additional Dependencies

Activate your existing `.venv` in **Command Prompt (CMD)** and install the web UI, search, and environment packages:

```bat
.venv\Scripts\activate
python -m pip install streamlit langchain-community ddgs python-dotenv pydantic pandas
```

## 2. Configure `.env` in Your Project Folder

Create (or update) a `.env` file in the same directory as `ipl_predictor_app.py` with your credentials. Make sure `.env` is listed in your `.gitignore` so keys are never pushed to GitHub:

```env
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=YOUR_LANGSMITH_API_KEY
LANGSMITH_PROJECT=caie-week2
```

## 3. Run the Web Application

Start the Streamlit server from your activated terminal:

```bat
streamlit run ipl_predictor_app.py
```

Your browser will open automatically to `http://localhost:8501`.

## 4. Usage & Tracing Verification

1. Choose your **Target Season** (e.g., `2027`) and **Historical Seasons Lookback Window** (e.g., `5` years) in the top control deck.
2. Click **Generate Forecast** to fetch live historical records and view the projected points table and win probability chart.
3. Switch to the **Head-to-Head Match Center** or **Franchise Trophy Cabinet** tabs to simulate fixtures or inspect franchise titles.
4. Open [smith.langchain.com](https://smith.langchain.com) under project `IPL Predictor App` to inspect the structured output traces, token counts, and latency for every forecast and match simulation.