Below is a revised `README.md` for your Python project, incorporating the details from `QuantUtilities.py` and adhering to your request to avoid including instructions on how to run the project. The README focuses on describing what the project does, its technical components, and its purpose, tailored for a GitHub audience. It also includes a mention of the hardcoded Excel table columns as required.

---

# Long-Short Cointegration Analysis

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-archived-yellow.svg)

This project implements a quantitative finance pipeline designed to identify cointegrated asset pairs for Long-Short trading strategies on the Brazilian stock exchange (B3). It processes historical price data from Tryd (a trading platform), performs statistical tests to detect cointegration, and generates detailed reports to select optimal asset pairs based on cointegration parameters, spread behavior, and Bollinger Bands' stability. The project was developed as an academic exercise and is archived as of April 2025.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technical Details](#technical-details)
- [Excel Output Structure](#excel-output-structure)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

## Overview
The Long-Short Cointegration Analysis project focuses on identifying pairs of B3-listed assets that exhibit cointegration, a statistical property indicating a stable long-term relationship between their prices. Such pairs are suitable for Long-Short trading strategies, where one asset is bought (long) and the other sold (short) to capitalize on mean-reverting spreads. The pipeline includes data migration from Tryd's CSV files, daily price updates, and comprehensive cointegration analysis.

The project comprises three main scripts:
1. **`migracao_unica.py`**: Performs a one-time migration of historical price data (closing, high, low) from Tryd's CSV files into a Python-compatible database.
2. **`migracao_diaria.py`**: Updates the database daily with the latest closing, high, and low prices from a predefined CSV file.
3. **`LSCointegracao.py`**: Executes cointegration tests, calculates trading metrics, and generates CSV reports for cointegrated pairs and residuals.

Additionally, utility functions in `QuantUtilities.py` support data processing and statistical calculations.

## Features
- **Data Migration and Updates**:
  - Imports historical price data from Tryd's CSV files, including date, closing, high, and low prices.
  - Supports daily updates to ensure the database reflects the latest market data.
  - Validates data integrity by checking for duplicates and synchronization issues.

- **Cointegration Analysis**:
  - Tests for cointegration using Phillips-Perron (PP) and KPSS tests to verify residual stationarity.
  - Employs Ordinary Least Squares (OLS) and Orthogonal Total Squares (OTS)/PCA regression to estimate hedge ratios.
  - Calculates Pearson correlation with confidence intervals to filter correlated pairs.

- **Spread and Trading Metrics**:
  - Monitors the spread (difference between asset prices adjusted by hedge ratio).
  - Computes half-life of mean reversion using lagged OLS regression.
  - Evaluates beta stability through rolling window regression and dispersion metrics.
  - Applies the Chow test to detect structural breaks in regression parameters.

- **Bollinger Bands Stability**:
  - Assesses the "horizontalness" of Bollinger Bands using configurable criteria (e.g., relative dispersion, mean value).
  - Filters pairs based on stable Bollinger Bands to ensure reliable trading signals.

- **Statistical Tests**:
  - Shapiro-Wilk test to verify normality of beta volatility.
  - Iterative testing with increasing sample sizes to ensure robustness.

- **Reporting**:
  - Generates CSV reports detailing cointegrated pairs, statistical metrics, and trading signals (buy/sell).
  - Outputs residuals for spread monitoring.
  - Includes comprehensive logging for debugging and execution tracking.

- **Utility Functions**:
  - Calculates the Relative Strength Index (RSI) for potential additional analysis.
  - Identifies maximum/minimum indices in price series.
  - Provides helper functions for timeframe formatting and Z-score calculations.

## Technical Details
The project leverages statistical and financial modeling to identify cointegrated pairs suitable for Long-Short strategies. Key components include:

- **Data Processing**:
  - Handles CSV files containing historical price data (date, closing, high, low) from Tryd.
  - Stores data in a local Python database with robust error handling for file I/O and encoding issues.
  - Supports configurable column selection (e.g., `Data`, `Fechamento`, `Maxima`, `Minima`).

- **Cointegration Tests**:
  - **Phillips-Perron (PP) Test**: Tests residual stationarity (null: non-stationary).
  - **KPSS Test**: Complements PP by testing stationarity as the null hypothesis.
  - **OLS Regression**: Estimates the relationship between asset prices and computes residuals.
  - **OTS/PCA**: Derives hedge ratios using eigenvectors from covariance matrices.

- **Statistical Metrics**:
  - **Pearson Correlation**: Filters pairs with a minimum correlation threshold and confidence intervals.
  - **Half-Life**: Measures mean reversion speed via OLS regression on lagged spread series.
  - **Beta Dispersion**: Assesses regression coefficient stability over rolling windows (30 periods, step of 2).
  - **Chow Test**: Detects structural breaks in regression parameters for robustness.
  - **Shapiro-Wilk Test**: Ensures normality of beta volatility for reliable metrics.

- **Bollinger Bands Horizontalness**:
  - Evaluates stability of Bollinger Bands using criteria like relative dispersion (`HORIZ_DISP_RELAT`), first value (`HORIZ_FIRST_VALUE`), last value (`HORIZ_LAST_VALUE`), or mean value (`HORIZ_MEAN_VALUE`).
  - Filters pairs with a horizontalness limiar (`LIMIAR_HORZ`) to ensure stable spreads.

- **Utility Functions**:
  - **RSI Calculation**: Computes the Relative Strength Index using exponential moving averages (EMA) with a configurable time window.
  - **Max/Min Index Finder**: Identifies the index of the maximum or minimum value in a price series.
  - **Z-Score Lookup**: Returns Z-scores for given p-values (e.g., 1.96 for 0.05, 2.58 for 0.01).
  - **Timeframe Formatter**: Converts timeframe constants to string representations (e.g., `D1` for daily).
  - **Data Reader**: Loads historical price data from CSV files with support for different encodings (Tryd or MT5).

- **Configuration**:
  - Parameters like sample size (`AMOSTRA_LONGA`, `TAM_AMOSTRA_UNIROOT`), test step size (`STEP_OF_TEST`), and critical p-values are defined in `QuantMT5ConstantesGlobais.py`.
  - Supports a predefined list of B3 assets (`LISTA_B3`).

- **Performance**:
  - Iteratively tests cointegration by increasing sample size in fixed steps.
  - Filters pairs with a minimum pass rate (e.g., 80%) across multiple tests.
  - Outputs metrics like pass rate, spread z-score, confidence intervals, and Bollinger Bands horizontalness.

## Excel Output Structure
The project generates CSV files that are designed to be imported into Excel for further analysis. The main output file, `Ativos_cointegrados_lista_YYYY_MM_DD_HH_MM_SS.csv`, contains cointegrated pairs with the following hardcoded columns:

| Column Name | Description |
|-------------|-------------|
| Numerador | Independent asset (e.g., stock ticker). |
| Preço_NUM | Placeholder for numerator price (set to `0`). |
| Preço_DEN | Placeholder for denominator price (set to `0`). |
| Ratio_Ult | Latest price ratio (`Numerador`/`Denominador`). |
| Ratio Inst | Instantaneous ratio formula (e.g., `=Stech|COT!Numerador.Ult/Stech|COT!Denominador.Ult`). |
| Ratio_medio | Z-score of the ratio based on rolling mean and standard deviation. |
| Ratio_2D_minus | Spread z-score based on mean and standard deviation of the spread. |
| Ratio_2D_plus | Relative dispersion of the ratio (100 * std/mean). |
| Ratio_3D_minus | Absolute relative dispersion of the spread (100 * std/mean). |
| Ratio_3D_plus | Number of weeks cointegrated. |
| Ratio_4D_minus | Optimal beta from OLS regression. |
| Ratio_4D_plus | Half-life of the spread. |
| Buy | Asset to buy (based on ratio deviation). |
| Nr_Cotas_Buy | Formula for number of shares to buy (e.g., `=MARRED($AL$1/S?,100)`). |
| Valor_Buy | Formula for buy value (e.g., `=AF?*S?`). |
| Sell | Asset to sell (based on ratio deviation). |
| Nr_Cotas_Sell | Formula for number of shares to sell (e.g., `=MARRED($AL$1/J?,100)`). |
| Valor_Sell | Formula for sell value (e.g., `=AI?*J?`). |
| (Unnamed) | Placeholder columns (set to `0`). |
| Beta_Normal | Normality of beta volatility (`SIM` or `NÃO`). |
| Vol_Beta | Volatility of beta (percentage). |
| Chow_Pass | Whether the Chow test passed (`SIM` or `NÃO`). |
| Nr_Periods_Spread | Number of periods with significant spread deviation. |
| IC_Corr | Confidence interval for Pearson correlation (e.g., `[lower - upper]`). |
| Alfa | Confidence level of the PP test (`95` or `99`). |
| Melhor_Periodo | Optimal sample size for cointegration. |
| Horizontalidade | Bollinger Bands horizontalness value. |

Additionally, `Ativos_cointegrados_residuos_YYYY_MM_DD_HH_MM_SS.csv` contains residuals for each pair, with columns:
- **Numerador**: Independent asset.
- **Denominador**: Dependent asset.
- **Residuos**: Pipe-separated z-scores of the spread, padded with zeros for shorter periods.

These files are saved in the `PLANILHAS` directory with timestamps for versioning.

## Project Structure
```
long-short-cointegration/
├── Database_Python/                # Python database with processed asset data
├── Database_Tryd/                  # Tryd's raw CSV files
├── LOGS/                           # Log files for execution tracking
├── PLANILHAS/                      # Output CSV reports
├── LSCointegracao.py               # Main cointegration analysis script
├── migracao_diaria.py              # Script for daily price updates
├── migracao_unica.py               # Script for one-time data migration
├── QuantMT5ConstantesGlobais.py    # Configuration constants
├── QuantUtilities.py               # Utility functions for data processing and statistics
├── README.md                       # This file
```

## Dependencies
- `pandas`: Data manipulation and CSV handling.
- `numpy`: Numerical computations.
- `scipy`: Statistical tests (e.g.,  - `statsmodels`: OLS regression and time-series analysis.
- `arch`: Unit root tests (Phillips-Perron, KPSS).
- `sklearn`: Linear regression.
- `warnings`: Suppresses specific warnings during execution.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author
- **Giovanni Leopoldo Rozza**
  - GitHub: [github.com/yourusername](https://github.com/yourusername)
  - Email: giovanni.rozza@example.com
  - LinkedIn: [linkedin.com/in/giovanni-rozza](https://linkedin.com/in/giovanni-rozza)

---

### Notes
- The status badge is set to "archived" as per your indication that this is an old project.
- The `Excel Output Structure` section details the hardcoded columns from `LSCointegracao.py`, specifically from the `ativos_cointegrados_csv` and `residuos_pass_csv` lists.
- `QuantUtilities.py` functions (e.g., RSI, `acha_idx_max_min`, `get_Z_alfa`) are described where relevant, but not all are directly used in the cointegration pipeline (e.g., RSI is not referenced in the main scripts).
- No replication instructions are included, as requested.
- Replace `yourusername` and contact details with your actual information.
- Add a `LICENSE` file to the repository if not already present.
- If you want to highlight specific aspects (e.g., academic context, specific B3 assets), let me know, and I can refine further!