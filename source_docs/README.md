# A District-Level CAMS Forecast-ERA5 Reanalysis PM-Based Air-Quality Proxy and Meteorological Dataset for Dhaka Division, Bangladesh (July 2015-December 2025)

District-level model-derived PM2.5, PM10 and meteorological estimates for all 13 Dhaka Division districts, 1 July 2015 to 31 December 2025 UTC. The hourly products contain 1,197,144 rows (92,088 per district). CAMS operational surface PM forecasts and ERA5 temperature, dewpoint and wind are aggregated using ADM2 polygon/grid intersection areas in EPSG:6933. PM concentrations are converted from kg/m3 to ug/m3. Relative humidity and wind metrics are derived deterministically. Retrospective US EPA 2024 PM breakpoints produce trailing 24-hour and Bangladesh-local daily PM_ONLY_AQI model proxies, not official monitor AQI. 10,647 paired PM observations at 819 step-0 valid times are withheld under a documented entire-grid-zero QC rule; original source zeros are preserved. No observations are invented or interpolated. BDT dates extend to 1 January 2026 because UTC+06:00 is used. The package includes CSV.gz, Parquet, a formatted XLSX, source archives, runnable offline code, tests, documentation and integrity evidence.

## Products

- `data/dhaka_hourly_core_2015_2025.csv.gz` and `.parquet`: 1,197,144 rows.
- `data/dhaka_hourly_extended_2015_2025.csv.gz` and `.parquet`: 1,197,144 rows.
- `data/dhaka_daily_bdt_all_dates_2015_2026.csv.gz` and `.parquet`: 49,894 rows.
- `data/dhaka_daily_bdt_complete_days_2015_2025.csv.gz` and `.parquet`: 39,234 rows.
- `data/dhaka_hourly_convenience.xlsx`: 16 sheets, including all district hourly records and local daily records.

## Interpretation

Processed PM has 10,647 missing values per pollutant from the documented step-0 QC. Extended data retains the original source values, forecast reference/lead and QC flag. Every timestamp remains present. At least 18 valid hours are required for a PM sub-index; complete-day data contains only 24 valid hours for both pollutants. AQI uses retrospective EPA 2024 PM breakpoints with truncation and half-up rounding; highest-segment extrapolation is uncapped above 500. This is not NowCast, full gas AQI or regulatory monitoring data.

CSV uses plain lossless decimal values and blank nulls; Excel displays two decimals without changing stored precision. UTC/BDT dates and coverage flags are explicit. See documentation/scientific_methodology.md and limitations.md.

## Reproduction and Deposit

Follow STEPS_TO_REPRODUCE.md. The 95-file roles/layout match the supplied Rajshahi reference after division-specific naming changes; schemas and scientific policy are not claimed identical. Four named authors, emails and ORCIDs are recorded in AUTHORS.md in the depositor-supplied order. This is a technically checked candidate, not an already published dataset. All-author approval and independent human accuracy/rights review remain mandatory. Data: CC BY 4.0; project code: MIT; upstream terms remain separate.
