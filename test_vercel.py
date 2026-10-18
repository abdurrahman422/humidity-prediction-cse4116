import json
import joblib
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from app import app, load_model
from humidity_model import ROOT, OUT, prepare_inputs

client = TestClient(app)
assert client.get("/").status_code == 200
assert "Machine Learning Laboratory" in client.get("/").text
assert len(client.get("/api/info").json()["districts"]) == 13
comparison = client.get("/api/comparison").json()
assert comparison["test_rows"] == 228072
assert comparison["selected_model"] == "Random Forest"
assert {row["model"] for row in comparison["models"]} == {"Linear Regression", "Random Forest", "LightGBM"}
for row in comparison["models"]:
    tn, fp, fn, tp = np.asarray(row["confusion_matrix"]).ravel()
    assert tn + fp + fn + tp == comparison["test_rows"]
    assert np.isclose(row["accuracy_percent"], 100 * (tn + tp) / comparison["test_rows"])
    assert np.isclose(row["F1"], 2 * tp / (2 * tp + fp + fn))
    assert np.isclose(row["MSE"], row["RMSE"] ** 2)
    assert all(np.isfinite(row[key]) for key in ["MAE", "RMSE", "R2", "accuracy_percent", "precision", "recall", "F1"])
assert 'id="error-chart"' in client.get("/").text
assert 'id="class-chart"' in client.get("/").text
assert 'id="r2-chart"' in client.get("/").text
values = {"temperature_c": 30, "dewpoint_c": 25, "district": "Dhaka", "month": 10, "hour": 22}
response = client.post("/api/predict", json=values)
assert response.status_code == 200
assert response.json()["humidity_pct"] == 74.6
for change in [{"dewpoint_c": 35}, {"month": 13}, {"hour": 24}, {"district": "Unknown"}]:
    assert client.post("/api/predict", json={**values, **change}).status_code == 400
assert client.post("/api/predict", content="invalid json").status_code == 400
assert client.post("/api/predict", json=[]).status_code == 400
assert client.post("/api/predict", content="x" * 5000).status_code == 400

original = joblib.load(OUT / "humidity_model.joblib")
saved = load_model()
sample = pd.read_parquet(ROOT / "data/dhaka_hourly_core_2015_2025.parquet",
    columns=["temperature_c", "dewpoint_c", "district", "datetime_utc"]).sample(200, random_state=42)
local = pd.to_datetime(sample.datetime_utc, utc=True).dt.tz_convert("Asia/Dhaka")
sample["month"] = local.dt.month
sample["hour"] = local.dt.hour
x = prepare_inputs(sample, saved["districts"])
assert np.allclose(original["model"].predict(x), saved["model"].predict(x), atol=1e-10)
print("Vercel API checks passed; compressed and original models agree on 200 records.")
