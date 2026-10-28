# UK Wind Generation: Forecast vs Actual

A web app that helps a UK energy utility make day-ahead power purchase
decisions. It shows the latest national wind generation forecast that was
available at decision time and measures how accurate such forecasts are
against actual generation.

- Scope: national level wind only, purchase decisions made in January 2026
  (delivery days 2 Jan to 1 Feb 2026)
- Data: Elexon BMRS only
  - Actuals: `FUELHH` (fuelType `WIND`)
  - Forecasts: `WINDFOR`

## Live app

Live link: TO BE ADDED

## Files and directories

```
.
├── README.md
├── docker-compose.yml     Runs backend and frontend with one command
├── vercel.json            Vercel build and routing configuration
├── requirements.txt       Python dependencies used by Vercel
├── api/
│   └── index.py           Vercel entry point (exposes the FastAPI app)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt       Runtime dependencies
│   ├── requirements-dev.txt   Adds pytest, httpx, requests
│   ├── app/
│   │   ├── main.py            FastAPI routes
│   │   ├── logic.py           Forecast selection and accuracy metrics
│   │   └── fetch_data.py      Downloads the data from Elexon into data/raw
│   └── tests/                 Automated tests (pytest)
├── data/
│   └── raw/                   actuals.csv and forecasts.csv from Elexon
└── frontend/                  React (Vite) app
    ├── Dockerfile, nginx.conf Build and serve the UI, forward /api to the backend
    └── src/
        ├── App.jsx            Page layout and state (delivery day, cutoff)
        ├── api.js             Calls to the backend API
        └── components/        Charts and metric cards
```

## How to run

### With Docker

```
docker compose up --build
```

Then open http://localhost:8080. Stop with `Ctrl+C`, then `docker compose down`.

### Without Docker

Backend (terminal 1):

```
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

Frontend (terminal 2):

```
cd frontend
npm ci
npm run dev
```

Open the URL that `npm run dev` prints (http://localhost:5173). The dev
server forwards `/api` calls to the backend on port 8000. To use another
backend port, set `API_TARGET` first, for example
`set API_TARGET=http://127.0.0.1:8001` on Windows.

### Tests

```
cd backend
pip install -r requirements-dev.txt
pytest
```

### Refreshing the data (optional)

The CSV files in `data/raw` are already included. To download them again
from Elexon:

```
cd backend
pip install -r requirements-dev.txt
python app/fetch_data.py
```

## API

All endpoints take an optional `cutoff_hour` (0 to 23, default 9).

| Endpoint | Returns |
|---|---|
| `GET /api/v1/health` | Health check |
| `GET /api/v1/comparison?date=YYYY-MM-DD` | Hourly forecast vs actual for one delivery day |
| `GET /api/v1/metrics` | MAE, RMSE, bias, MAPE and error limits (optional `start`, `end`) |
| `GET /api/v1/errors/daily` | MAE and bias for each delivery day |
| `GET /api/v1/errors/by-hour` | MAE and bias by hour of day |
| `GET /api/v1/errors/distribution` | Histogram of hourly errors (1,000 MW bins) |

## How it works

- **Decision cutoff:** the day-ahead decision is made on the day before
  delivery. The default cutoff is 09:00 UTC and it can be changed in the UI.
- **Which forecast is used:** for each target hour, the app uses the latest
  forecast whose `publishTime` is at or before the cutoff. A forecast
  published after the cutoff is never used, because it would not have been
  available when the decision was made.
- **Hourly actuals:** forecasts are hourly and actuals are half-hourly, so
  each hour's actual is the average of the two half-hour `FUELHH` values.
- **Metrics:** MAE, RMSE, bias (forecast minus actual), MAPE (hours with zero
  actual output are skipped), and a 95% over-forecast limit (in 95% of hours
  the forecast overshoots by less than this value). The UI also shows error
  per delivery day, error by hour of day, and the error distribution.
- **Architecture:** FastAPI backend (pandas for the calculations) and a React
  (Vite) frontend. With Docker, nginx serves the UI and forwards `/api` to
  the backend container. On Vercel, `api/index.py` exposes the same FastAPI
  app as a serverless function.

## Assumptions

- The cutoff time was not given, so it is an assumption: 09:00 UTC on the
  day before delivery, adjustable in the UI. For the default data, a cutoff
  of 08:00 gives the same result, because the same forecast (published at
  07:30) is the latest one before either time.
- "Purchase decisions made in January 2026" is read as decisions on 1 to
  31 Jan, each for the next day's delivery, so delivery days are 2 Jan to
  1 Feb 2026 (744 hours).
- In January the UK is on GMT, so UK time equals UTC. All times in the app
  and in the data are UTC.
- Forecasts published after the target hour are ignored, since they could
  not have been used for a decision.

## Findings for January 2026

Forecast as known at the 09:00 UTC cutoff, over 744 hours:

| Metric | Value |
|---|---|
| MAE | about 2,039 MW |
| RMSE | about 2,505 MW |
| Bias | about +1,748 MW (forecast higher than actual) |
| MAPE | about 22% |
| 95% over-forecast limit | about 5,283 MW |

- On average the forecast is above actual output, so a buyer relying on the
  forecast alone would tend to under-buy.
- The bias is not constant. It is close to zero on some days (for example
  5, 10 and 14 Jan) and large on days when the forecast predicted very high
  output (11 to 12 Jan and 28 Jan: roughly +4,800 to +5,400 MW; 27 Jan:
  about +3,500 MW).
- On 12 Jan the actual output stays between about 13,700 and 15,400 MW all
  day while the forecast is between about 16,300 and 20,900 MW. A possible
  cause is curtailment of wind during grid constraints, but this cannot be
  confirmed with only the two allowed datasets.
- The dashboard and the API return these same numbers.

## Limitations

- Only the two Elexon datasets are used, at national level.
- Only January 2026 purchase decisions are covered.
- No other data (weather, prices, curtailment) is used, so the reasons for
  forecast errors are not explained, only measured.

## AI tools used

AI assistants were used while building this project: Claude (design,
debugging, code and documentation help) and an Antigravity coding agent
(code changes, tests and verification runs).