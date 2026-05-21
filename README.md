# Food-Additives

A Streamlit + FastAPI web app to search foods and visualize calories, macronutrients, micronutrients, and fiber.

## Features

- Search by food name (for example: `banana`, `salmon`, `brown rice`).
- Retrieve nutrition from USDA FoodData Central.
- Show calories, macros, and fiber.
- Plot macro split (pie chart) and micros (bar chart).
- Browse top matches and inspect raw JSON.

## Project structure

```text
backend/
  app.py
  requirements.txt
  .env.example
frontend/
  app.py
  requirements.txt
```

## Prerequisites

- Python 3.10+
- USDA FoodData Central API key

Get an API key from the USDA FoodData Central website.

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set USDA_API_KEY
uvicorn app:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## Frontend setup (Streamlit)

Open a second terminal:

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

Then open `http://localhost:8501`.

## Deploy to Streamlit Community Cloud

This repository uses a two-service architecture (Streamlit frontend + FastAPI backend).
For Streamlit Cloud deployment, first deploy backend to a public host (for example Render/Railway/Fly.io), then set that URL in the app sidebar.

## GitHub publish steps

Run these commands locally after creating a GitHub repository:

```bash
git init
git add .
git commit -m "Initial nutrition web app"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```
