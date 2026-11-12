# Week 2, Day 3: Trace a LangChain App with LangSmith

The application code is entirely in `traced_app.py`. It uses `ChatOpenAI`, sends
three different prompts in one execution, and prints every prompt and answer.
It also prints actual returned token usage and locally measured elapsed time.
Local elapsed time includes client overhead and retries, so use the LangSmith
latency value when completing the assignment's dashboard observations.

There are no tracing imports, callbacks, decorators, or tracing settings in the
Python file. Tracing is enabled only through environment variables, as required.

## 1. Prepare your Windows environment

Save `traced_app.py` in your project folder and open that folder in VS Code.
The commands below are for **Command Prompt (CMD)**, matching your screenshots.

For a new environment:

```bat
py -3.13 -m venv .venv
.venv\Scripts\activate
python --version
python -m pip install --upgrade pip
python -m pip install langchain langchain-openai
```

If you already created `.venv` with Python 3.13, skip creation and activate it.
If an older `venv` is currently active, run `deactivate` first.
In VS Code, use Ctrl+Shift+P -> Python: Select Interpreter and choose
`.venv\Scripts\python.exe`.

## 2. Configure both keys and the named project

Use your own OpenAI API key and your own LangSmith API key. Replace the placeholders
locally; do not put real keys in the Python file, GitHub, or screenshots.
Run these commands in the same terminal that will run the app:

```bat
set "OPENAI_API_KEY=YOUR_OPENAI_API_KEY"
set "LANGSMITH_TRACING=true"
set "LANGSMITH_API_KEY=YOUR_LANGSMITH_API_KEY"
set "LANGSMITH_PROJECT=caie-week2"
```

If using **PowerShell** instead, the equivalent settings are:

```powershell
$env:OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
$env:LANGSMITH_TRACING="true"
$env:LANGSMITH_API_KEY="YOUR_LANGSMITH_API_KEY"
$env:LANGSMITH_PROJECT="caie-week2"
```

These settings apply to the current terminal session. A new terminal needs them
again. This solution does not load a `.env` file.

For a non-default LangSmith region, also set `LANGSMITH_ENDPOINT` to the API
endpoint shown in your LangSmith workspace settings. If your key belongs to
multiple workspaces, set `LANGSMITH_WORKSPACE_ID` to the intended workspace ID.

## 3. Check configuration before running

This terminal-only check does not alter the application or enable tracing in code.
It verifies the flag, project, and presence of keys without printing the keys:

```bat
python -c "import os; assert os.getenv('LANGSMITH_TRACING', '').lower() == 'true', 'Tracing flag is off'; assert os.getenv('LANGSMITH_PROJECT') == 'caie-week2', 'Project mismatch'; assert os.getenv('LANGSMITH_API_KEY'), 'Missing LangSmith key'; assert os.getenv('OPENAI_API_KEY'), 'Missing OpenAI key'; print('Environment checks passed')"
```

Passing this check confirms configuration, not successful trace delivery or key
validity. To verify delivery, run the application and find its new runs in the
dashboard. An answer printed in the terminal alone does not prove tracing worked.

## 4. Run the app

```bat
python traced_app.py
```

Let the process finish normally. A successful execution makes three model calls.
The real answers, timings, and token counts depend on the API responses; no sample
measurements are fabricated. Each call is independent and does not carry previous
answers as conversation history.

If you get an authentication error, check the relevant API key. A quota/billing
error requires available OpenAI API credit; a ChatGPT subscription alone does not
provide API credit. If the run fails partway, fix the error and rerun; partial runs
can remain in the dashboard, so select the three calls from the successful execution.

## 5. Inspect LangSmith and collect evidence

1. Open https://smith.langchain.com and select your intended workspace.
2. Open the tracing project `caie-week2` and refresh after the app finishes.
3. Locate the three new successful calls by timestamp and prompt input. They may
   all have the model's default run name rather than numbered names.
4. Capture a screenshot of the project showing those three runs.