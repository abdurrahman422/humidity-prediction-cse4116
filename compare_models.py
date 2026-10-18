import hashlib
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import precision_score, recall_score, confusion_matrix
from lightgbm import LGBMRegressor
from humidity_model import DATA, OUT, ROOT, prepare_inputs, evaluate


def compare():
    data = pd.read_parquet(DATA, columns=["district", "datetime_utc", "temperature_c",
                                        "dewpoint_c", "relative_humidity_pct"])
    time = pd.to_datetime(data.datetime_utc, utc=True)
    local = time.dt.tz_convert("Asia/Dhaka")
    data["month"], data["hour"] = local.dt.month, local.dt.hour
    train = time < "2023-01-01"
    valid = (time >= "2023-01-01") & (time < "2024-01-01")
    test = time >= "2024-01-01"
    saved = joblib.load(ROOT / "deployment/humidity_model.joblib.gz")
    x = prepare_inputs(data, saved["districts"])
    y = data.relative_humidity_pct
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": saved["model"],
        "LightGBM": LGBMRegressor(n_estimators=350, num_leaves=31, learning_rate=0.06,
                                  random_state=42, n_jobs=4, verbosity=-1)
    }
    rows = []
    actual = y[test].to_numpy()
    for name, model in models.items():
        if name != "Random Forest":
            print("Training", name, flush=True)
            model.fit(x.loc[train], y.loc[train])
        prediction = np.clip(model.predict(x.loc[test]), 0, 100)
        validation = np.clip(model.predict(x.loc[valid]), 0, 100)
        error = actual - prediction
        truth, decision = actual >= 85, prediction >= 85
        metrics = evaluate(actual, prediction)
        rows.append({"model": name, "training_rows": 150000 if name == "Random Forest" else int(train.sum()),
            "validation_MAE": float(np.mean(np.abs(y[valid].to_numpy() - validation))),
            "MAE": metrics["MAE"], "RMSE": metrics["RMSE"], "R2": metrics["R2"],
            "MSE": float(np.mean(error ** 2)), "MAPE_percent": float(np.mean(np.abs(error) / actual) * 100),
            "accuracy_percent": metrics["high_humidity_accuracy_percent"],
            "F1": metrics["high_humidity_F1"],
            "precision": float(precision_score(truth, decision, zero_division=0)),
            "recall": float(recall_score(truth, decision, zero_division=0)),
            "within_1pp_percent": metrics["within_1pp_percent"],
            "confusion_matrix": confusion_matrix(truth, decision, labels=[False, True]).tolist()})
        print(name, "MAE:", metrics["MAE"], "F1:", metrics["high_humidity_F1"], flush=True)
    selected = min(rows, key=lambda row: row["validation_MAE"])["model"]
    assert selected == "Random Forest", "Review model selection before updating the prediction form"
    summary = json.loads((OUT / "summary.json").read_text())
    forest = next(row for row in rows if row["model"] == selected)
    assert np.isclose(forest["MAE"], summary["MAE"], atol=1e-10)
    result = {"task": "Same-time relative humidity estimation", "selected_model": selected,
        "inputs": ["Temperature", "Dewpoint", "District", "Month", "Hour (Bangladesh time)"],
        "validation_year": 2023, "test_years": "2024–2025", "test_rows": int(test.sum()),
        "class_threshold": 85, "models": rows,
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "notes": "Same test rows and features for every model. Training budgets differ: Random Forest 150,000 rows; others 855,192. Target humidity is formula-derived. Scores measure estimation, not next-hour forecasting. The evaluation years were inspected during development."}
    (OUT / "model_comparison.json").write_text(json.dumps(result, indent=2), encoding="utf8")
    pd.DataFrame([{k: v for k, v in row.items() if k != "confusion_matrix"} for row in rows]).to_csv(
        OUT / "model_comparison.csv", index=False)
    print("Saved comparison for", result["test_rows"], "evaluation records.", flush=True)


if __name__ == "__main__":
    compare()
