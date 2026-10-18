from functools import lru_cache
import json
import logging
import joblib
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from humidity_model import ROOT, OUT, predict

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@lru_cache(maxsize=1)
def load_model():
    saved = joblib.load(ROOT / "deployment/humidity_model.joblib.gz")
    saved["model"].n_jobs = 1
    return saved


@app.get("/")
def home():
    return FileResponse(ROOT / "humidity_ui.html")


@app.get("/api/info")
def info():
    saved = load_model()
    metrics = json.loads((OUT / "summary.json").read_text())
    return {"districts": saved["districts"], "metrics": metrics}


@app.post("/api/predict")
async def prediction(request: Request):
    try:
        body = await request.body()
        if len(body) > 4096:
            raise ValueError("Input is too large")
        values = json.loads(body)
        if not isinstance(values, dict):
            raise ValueError("Expected the five form inputs")
        return predict(values, load_model())
    except (ValueError, TypeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception:
        logging.exception("Humidity prediction failed")
        raise HTTPException(status_code=503, detail="Prediction is temporarily unavailable")


@app.get("/api/comparison")
def comparison():
    return json.loads((OUT / "model_comparison.json").read_text(encoding="utf8"))
