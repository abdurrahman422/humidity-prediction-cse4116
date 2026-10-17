from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, f1_score

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "humidity_outputs"
DATA = ROOT / "data/dhaka_hourly_core_2015_2025.parquet"


def evaluate(actual, prediction):
    actual = np.asarray(actual)
    prediction = np.asarray(prediction)
    return {"MAE": float(mean_absolute_error(actual, prediction)),
            "RMSE": float(np.sqrt(mean_squared_error(actual, prediction))),
            "R2": float(r2_score(actual, prediction)),
            "within_1pp_percent": float(np.mean(np.abs(actual - prediction) <= 1) * 100),
            "high_humidity_accuracy_percent": float(accuracy_score(actual >= 85, prediction >= 85) * 100),
            "high_humidity_F1": float(f1_score(actual >= 85, prediction >= 85, zero_division=0))}


def prepare_inputs(data, districts):
    x = data[["temperature_c", "dewpoint_c"]].astype(float).copy()
    x["dewpoint_depression_c"] = x.temperature_c - x.dewpoint_c
    for name, period in [("month", 12), ("hour", 24)]:
        x[name + "_sin"] = np.sin(2 * np.pi * data[name] / period)
        x[name + "_cos"] = np.cos(2 * np.pi * data[name] / period)
    for name in districts:
        x["district_" + name] = (data.district == name).astype(float)
    return x


def train():
    data = pd.read_parquet(DATA)
    time = pd.to_datetime(data.datetime_utc, utc=True)
    local_time = time.dt.tz_convert("Asia/Dhaka")
    data["month"] = local_time.dt.month
    data["hour"] = local_time.dt.hour
    columns = ["temperature_c", "dewpoint_c", "relative_humidity_pct"]
    assert data[columns].notna().all().all(), "Missing values need review"
    assert np.isfinite(data[columns]).all().all(), "Non-finite values found"
    assert not data.duplicated(["district", "datetime_utc"]).any()
    train_rows = time < "2023-01-01"
    test_rows = time >= "2024-01-01"
    districts = sorted(data.loc[train_rows, "district"].unique())
    x = prepare_inputs(data, districts)
    y = data.relative_humidity_pct
    rows = data.index[train_rows].to_numpy()
    rows = np.sort(np.random.default_rng(42).choice(rows, 150000, replace=False))
    model = RandomForestRegressor(n_estimators=60, max_depth=18,
                                 min_samples_leaf=3, random_state=42, n_jobs=4)
    model.fit(x.loc[rows], y.loc[rows])
    prediction = np.clip(model.predict(x.loc[test_rows]), 0, 100)
    metrics = evaluate(y[test_rows], prediction)
    limits = {c: {"min": float(data.loc[train_rows, c].min()),
                  "max": float(data.loc[train_rows, c].max())} for c in columns[:2]}
    OUT.mkdir(exist_ok=True)
    joblib.dump({"model": model, "districts": districts, "limits": limits,
                 "feature_columns": list(x.columns)}, OUT / "humidity_model.joblib")
    (OUT / "summary.json").write_text(json.dumps(metrics, indent=2))
    print(metrics)
    print("Training complete. Restart the app to load this model.")


def predict(values, saved):
    inputs = {}
    for name in ["temperature_c", "dewpoint_c", "month", "hour"]:
        value = values.get(name)
        if isinstance(value, bool):
            raise ValueError("Invalid number: " + name)
        try:
            inputs[name] = float(value)
        except (TypeError, ValueError):
            raise ValueError("Invalid number: " + name)
        if not np.isfinite(inputs[name]):
            raise ValueError("Inputs must be finite numbers")
    temperature = inputs["temperature_c"]
    dewpoint = inputs["dewpoint_c"]
    if not -60 <= temperature <= 60 or not -80 <= dewpoint <= 60:
        raise ValueError("Temperature or dewpoint is outside the allowed range")
    if dewpoint > temperature:
        raise ValueError("Dewpoint must not exceed temperature")
    if not inputs["month"].is_integer() or not 1 <= inputs["month"] <= 12:
        raise ValueError("Month must be from 1 to 12")
    if not inputs["hour"].is_integer() or not 0 <= inputs["hour"] <= 23:
        raise ValueError("Hour must be from 0 to 23")
    district = values.get("district")
    if district not in saved["districts"]:
        raise ValueError("Select a supported district")
    inputs["district"] = district
    x = prepare_inputs(pd.DataFrame([inputs]), saved["districts"])
    result = float(np.clip(saved["model"].predict(x[saved["feature_columns"]])[0], 0, 100))
    warning = ""
    for name in ["temperature_c", "dewpoint_c"]:
        limit = saved["limits"][name]
        if not limit["min"] <= inputs[name] <= limit["max"]:
            warning = "Input outside the training range; this estimate may be unreliable."
    return {"humidity_pct": round(result, 2), "warning": warning}


if __name__ == "__main__":
    train()
