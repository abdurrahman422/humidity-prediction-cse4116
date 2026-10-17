import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import joblib
import numpy as np
from humidity_model import OUT, predict, evaluate

saved = joblib.load(OUT / "humidity_model.joblib")
values = {"temperature_c": 30, "dewpoint_c": 25, "district": "Dhaka", "month": 10, "hour": 22}
result = predict(values, saved)
assert abs(result["humidity_pct"] - 74.61) < 0.1
assert predict({**values, "dewpoint_c": 25, "temperature_c": 25}, saved)["humidity_pct"] > 99
for change in [{"dewpoint_c": 35}, {"month": 13}, {"hour": 24},
               {"district": "Unknown"}, {"temperature_c": float("nan")}]:
    try:
        predict({**values, **change}, saved)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid input accepted")
metrics = evaluate([80, 90], [80, 90])
assert metrics["MAE"] == 0 and metrics["high_humidity_F1"] == 1
base = "http://127.0.0.1:8765"
info = json.load(urlopen(base + "/api/info"))
assert len(info["districts"]) == 13
request = Request(base + "/api/predict", json.dumps(values).encode(), {"Content-Type": "application/json"})
assert json.load(urlopen(request))["humidity_pct"] == result["humidity_pct"]
page = urlopen(base).read().decode()
assert "Machine Learning Laboratory" in page and 'lang="en"' in page
assert "/report" not in page and "Presentation guide" not in page
try:
    urlopen(base + "/report")
except HTTPError as error:
    assert error.code == 404
else:
    raise AssertionError("Old report route remains")
print("Input validation, saved model, metrics and local app checks passed.")
