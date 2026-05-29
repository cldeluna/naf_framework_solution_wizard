# Running the NAF Scripts

The scripts need to be installed before they can be run with `uv run`. Here are the correct commands:

## From the Project Root

### Install and Run API
```bash
# Install the project in editable mode (creates the scripts)
uv sync --dev

# Now run the API
uv run naf-api
```

### Install and Run Streamlit App
```bash
# Install the project in editable mode (creates the scripts)
uv sync --dev

# Now run the Streamlit app
uv run naf-wizard
```

## Alternative: Direct Commands

If you prefer not to install the scripts, you can run them directly:

### Run API Directly
```bash
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Run Streamlit Directly
```bash
uv run streamlit run pages/20_NAF_Solution_Wizard.py
```

## From Any Directory

Once installed, the scripts will be available in the virtual environment:

```bash
# Activate the virtual environment first
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Then run the scripts
naf-api
naf-wizard
```

## Troubleshooting

If you get "No such file or directory" error:
1. Make sure you're in the project root directory
2. Run `uv sync --dev` to install the scripts
3. Try running the command again

If you still have issues, use the direct commands shown above.
