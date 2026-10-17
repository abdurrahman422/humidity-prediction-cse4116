# Scientific Methodology

## Scope and Spatial Extraction

All 13 Dhaka Division ADM2 districts; UTC 2015-07-01 00:00 through 2025-12-31 23:00, 92,088 hours per district. Source-defined district geometry is fixed to geoBoundaries v5.0.0 (underlying boundary year 2020). Grid cells are defined by half-spacing edges on the native regular latitude/longitude axes. Intersection/polygon areas are measured in EPSG:6933. Registered full-polygon weights are independently checked against deposited geometries, then normalized for extraction after near-complete full-polygon coverage has been established. Valid contributing area must be >=0.95; missing cells are not zero-filled. All observed grids pass. Reproduction verifies units, dimensions, source hashes and forecast valid/reference/lead times.

## Source Units and PM QC

CAMS pm2p5/pm10 are surface kg m**-3, multiplied by 1e9 to ug/m3. Total-column gases are excluded. Both source PM grids being entirely zero at lead 0 triggers DHAKA_PM_STEP0_ENTIRE_GRID_ZERO_V1. This is an evidence-based interpretation consistent with ECMWF's documented step-0 bug, not a case-specific confirmation from ECMWF. Withhold processed PM as null/PENDING_SOURCE_DATA and retain source concentrations, forecast lead/reference and a boolean flag. There are 819 affected valid times (2015-07-01 to 2017-09-26) and 10,647 district records per pollutant. Nothing is interpolated. Subsequent leads and nonmatching zeros are not removed by this rule. Source evidence remains byte-identical.

## Meteorology

ERA5 2 m temperature/dewpoint: K minus 273.15. Relative humidity of the aggregated temperatures uses 100*exp(17.67*Td/(Td+243.5))/exp(17.67*T/(T+243.5)), with Celsius inputs, and is clipped to [0,100]; the extended product retains the unclipped value. This is not a direct humidity observation or the mean of grid-cell RH. Wind speed=sqrt(u10^2+v10^2); meteorological from-direction=(degrees(atan2(-u10,-v10))+360) modulo 360, based on area-weighted wind components. No vector values are complex numbers.

## AQI Proxy

Trailing windows contain the current and previous 23 indexed hours; at least 18 nonmissing PM values are required per pollutant. PM2.5 mean is truncated to one decimal, PM10 to an integer. US EPA 2024 concentration intervals map by linear interpolation to integer sub-indices, rounding exact halves upward. PM2.5 intervals: 0-9.0, 9.1-35.4, 35.5-55.4, 55.5-125.4, 125.5-225.4, 225.5-325.4 ug/m3. PM10: 0-54, 55-154, 155-254, 255-354, 355-424, 425-604. Index intervals: 0-50, 51-100, 101-150, 151-200, 201-300, 301-500. Above the top concentration, the highest segment is extrapolated without a cap. The maximum available PM sub-index is the proxy; PM2.5 wins ties. If neither is available, the proxy/category/dominant pollutant are null/blank. Full 24-hour coverage is distinguished from provisional 18-23-hour coverage. It is not an hourly regulatory NowCast.

Daily products group actual UTC observations by Asia/Dhaka calendar date (UTC+06:00). Concentration/weather means use available observations; pollutant sub-indices are null below 18 valid hours. A day is complete only with 24 valid PM observations for both pollutants. The first local day contains 18 indexed hours but 17 valid PM hours after QC; the final local date 2026-01-01 contains six indexed hours. Their PM AQI is withheld. BDT dates beyond 2025 are the UTC boundary's timezone conversion, not extended source coverage.

EPA 2024 is applied retrospectively throughout the record; this is not historical Bangladesh regulatory AQI. CAMS is an operational forecast product with changing model versions, not a homogeneous long-term reanalysis or ground monitoring measurement. PM_ONLY_AQI excludes CO/NO2/O3/SO2.

## References

- ECMWF source-zero issue: https://forum.ecmwf.int/t/aerosol-optical-depth-aod-and-particulate-matter-pm10-pm2-5-at-forecast-step-0-all-values-are-zero/1556
- EPA Technical Assistance Document: https://document.airnow.gov/technical-assistance-document-for-the-reporting-of-daily-air-quailty.pdf
- Provider attribution and terms: ../RESEARCH_PROVENANCE.md

## Source Precision-scale Inconsistencies

Six district rows at 2025-07-08 00 UTC have PM2.5 greater than PM10 by at most 0.0000896583073 ug/m3; the original float32 CAMS source also contains this ordering reversal. Fifty-nine district rows have dewpoint above temperature by at most 0.0018302485 K, giving raw derived RH up to 100.0117165%. The existing derived-RH rule clips it to 100%, while original temperature/dewpoint and raw RH remain unchanged in the extended product. These small inconsistencies are consistent with source model/encoding precision effects, but their exact cause is not established. They are disclosed, not silently corrected or converted to invented observations. Row-level records are in `quality/aqi_validation.csv` and `quality/humidity_validation.csv`; join by `district` and `datetime_utc`.
