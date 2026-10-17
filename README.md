# Machine Learning Laboratory (CSE 4116)

Double-click `Start_Humidity_App.cmd`, then open http://127.0.0.1:8765.
Enter temperature, dewpoint, district, month and hour to estimate humidity.

For Google Colab: upload `Humidity_Prediction.ipynb` and select Runtime -> Run all.
The notebook contains data loading, preprocessing, training, evaluation and a form.
`humidity_outputs/model_comparison.csv` can be imported into Google Sheets.

For a fresh download of this repository:

1. Install Python and run `python -m pip install -r requirements.txt`.
2. Download `dhaka_hourly_core_2015_2025.parquet` from the source DOI below into `data/`.
3. Run `python humidity_model.py` to create the saved model locally.
4. Run `python humidity_server.py --open` to open the application.

The large dataset and trained `.joblib` artifact are excluded from GitHub.
The Colab notebook can download the dataset and train the model independently.

To retrain locally: `python humidity_model.py` or `Train_Humidity_Model.cmd`.
To check the running app: `python test_humidity.py`.
Install packages if needed: `python -m pip install -r requirements.txt`.

MAE/RMSE are percentage points; accuracy/F1 refer only to the RH >=85% decision.
Source humidity is derived from temperature/dewpoint; this is estimation, not future weather forecasting.
Evaluation years were inspected during development; independent validation is still needed.
Source DOI: https://doi.org/10.17632/htz4fhttr4.1 (CC BY 4.0). Original attribution and licence: source_docs.
