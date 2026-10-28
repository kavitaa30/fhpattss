FROM python:3.12-slim

WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Layout inside the container: /app/backend/app and /app/data
# (logic.py finds the CSVs at <repo root>/data/raw)
COPY backend/app /app/backend/app
COPY data /app/data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]