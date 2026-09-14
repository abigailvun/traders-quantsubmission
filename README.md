# Quantitative Research Assessment: Delta-Hedged Short Put VRP Strategy

## ⚠️ Scope Disclaimer
> **Important Note:** Due to endpoint limitations encountered during historical contract retrieval and time constraints near the submission deadline, the script (`worked.py`) is restricted to executing on current/present-day market data rather than a complete multi-year historical backtest. This repository is submitted as a structural framework, methodology demonstration, and proof-of-concept for delta-hedged option execution. 
> 
> (P.S. I was also sick after friday so I wasn't able to do alot of the work)

---

## Overview
This repository contains the code, decision logs, and experiment records investigating the equity Volatility Risk Premium (VRP) using short out-of-the-money (OTM) put options combined with dynamic delta hedging.

## Repository Structure
* `worked.py` - Main script executing market data retrieval, implied volatility calculation, delta hedging, and daily rebalancing logic.
* `decision_log.csv` - Structured record of important decisions, endpoint hurdles, and pivots made throughout the project.
* `experiment_record.csv` - Log of meaningful experiments performed, including unsuccessful or modified approaches.
* `REPORT.md` - Concise final research report detailing findings, methodology, and limitations.
* `still_testing.py` - Experimental script used to test historical contract looping combined with daily aggregate endpoints (`CLIENT.get_daily_open_close_agg`). Left in the repository to document the attempt at historical backtesting, which ultimately ran too slow due to individual API request bottlenecks under time constraints.

---

## Setup Instructions

### 1. Clone the Repository
Clone this repository to your local environment.

### 2. Install Required Packages
Ensure you have Python installed, then install the required dependencies:
```bash
pip install massive-sdk fredapi numpy pandas scipy yfinance python-dotenv


## 5. Assistance and Source Disclosure

**Academic papers consulted:**
* Black, F., & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities. *Journal of Political Economy*, 81(3), 637-654.
* Bakshi, G., & Kapadia, N. (2003). Delta-Hedged Gains and the Negative Market Volatility Risk Premium. *Review of Financial Studies*, 16(2), 527-566.
* Rubinstein, M. (1994). Implied Binomial Trees. *Journal of Finance*, 49(3), 771-818.

**External datasets used:**
* Federal Reserve Economic Data (FRED) - Secured Overnight Financing Rate (SOFR) series.
* Yahoo Finance (yfinance) - Historical daily adjusted close stock prices for simulation paths.

**Existing repositories or code consulted:**
* Official Massive SDK Python client documentation and quickstart guides.

**Tutorials or articles used:**
* SciPy documentation on `scipy.optimize.brentq` for Implied Volatility root-finding.
* Quantitative finance guides on delta-neutral option portfolio rebalancing.

**AI tools used & what each AI tool was used for:**
* Gemini: Used as an AI collaborator to brainstorm research hypotheses, assist with structural code refactoring for API endpoints, format decision and experiment logs, and draft report sections and documentation templates.

**Any assistance received from another person:**
* Completed individually; no human assistance was received.