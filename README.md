# Machine Learning Laboratory (CSE 4116)

Double-click `Start_Humidity_App.cmd`, then open http://127.0.0.1:8765.
Enter temperature, dewpoint, district, month and hour to estimate humidity.

For Google Colab: upload `Humidity_Prediction.ipynb` and select Runtime -> Run all.
The notebook contains data loading, preprocessing, training, evaluation and a form.
`humidity_outputs/model_comparison.csv` can be imported into Google Sheets.

For a fresh download of this repository:

1. Install Python and run `python -m pip install -r requirements-training.txt`.
2. Download `dhaka_hourly_core_2015_2025.parquet` from the source DOI below into `data/`.
3. Run `python humidity_model.py` to create the saved model locally.
4. Run `python humidity_server.py --open` to open the application.

The large dataset and uncompressed `.joblib` artifact are excluded from GitHub.
The Colab notebook can download the dataset and train the model independently.

For Vercel, import this repository with the FastAPI framework preset. `app.py`
serves the same form and prediction API. The losslessly compressed Random Forest
in `deployment/` is included; training does not run on Vercel. Python 3.12 and
runtime dependencies are specified in `.python-version` and `requirements.txt`.

The live model-comparison charts use `humidity_outputs/model_comparison.json`.
Run `python compare_models.py` with the training dependencies to regenerate
same-time estimation metrics for Linear Regression, Random Forest and LightGBM.
Accuracy/F1 are for the separate RH >=85% decision; MAE/RMSE/R2 evaluate regression.
These are not the next-hour forecasting experiment's scores.

To retrain locally: `python humidity_model.py` or `Train_Humidity_Model.cmd`.
To check the running app: `python test_humidity.py`.
Install training packages if needed: `python -m pip install -r requirements-training.txt`.

MAE/RMSE are percentage points; accuracy/F1 refer only to the RH >=85% decision.
Source humidity is derived from temperature/dewpoint; this is estimation, not future weather forecasting.
Evaluation years were inspected during development; independent validation is still needed.
Source DOI: https://doi.org/10.17632/htz4fhttr4.1 (CC BY 4.0). Original attribution and licence: source_docs.
