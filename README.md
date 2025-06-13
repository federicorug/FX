# Bloomberg FX Derivatives Pricing Framework

This repository provides a Python-based framework for building **FX  curves** using the **Bloomberg API**, and for **pricing derivatives** on top of those market inputs. The current version includes construction of:

- **FX Spot & Forward Curve**
- **EUR Interest Rate Curve**
- **USD Interest Rate Curve**
- **FX Volatility Surface**

Once the market environment is built, the system allows for **derivatives pricing** (e.g., vanilla FX options) using industry-standard models.

---

## 📈 Current Features

### ✅ Market Data Bootstrapping (via Bloomberg API)
- Fetch FX spot and forward points
- Build FX forward curve (EUR/USD)
- Construct zero rate curves for:
  - EUR (e.g., EURIBOR or ESTR-based)
  - USD (e.g., SOFR-based)
- Retrieve implied volatility surface for EUR/USD:
  - Multiple tenors and deltas
  - Surface interpolation

### ✅ Derivative Pricing
- Garman-Kohlhagen pricing for FX options
- Support for European vanilla options

---

## 🚧 Roadmap / To-Do

This project is under active development. Planned expansions include:

- Add support for other FX pairs (e.g., GBP/USD, USD/JPY)
- Price exotic derivatives (barriers, digitals)
- Integrate QuantLib for more advanced analytics

---

## 🧰 Tech Stack

- **Python 3.12.7**
- **Bloomberg Python API (blpapi)**
- **Pandas / NumPy / SciPy**
- **QuantLib** (optional, for advanced pricing)
- **datetime**

---
