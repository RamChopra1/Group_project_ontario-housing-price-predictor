# GTA Home Price Predictor

A Streamlit web app that predicts residential sold prices in the Greater Toronto Area using a trained Linear Regression model.

---

## Files Required

Make sure all of these are in the same folder before running:

```
app.py
model.pkl
scaler.pkl
feature_columns.pkl
requirements.txt
```

---

## Setup and Installation

### Step 1 — Make sure Python is installed

You need Python 3.10 or higher. Check your version:

```bash
python --version
```

If not installed, download from https://www.python.org/downloads/

---

### Step 2 — Install dependencies

Navigate to the folder where your files are:

```bash
cd path/to/your/folder
```

Then install all required packages:

```bash
pip install -r requirements.txt
```

If `pip` is not recognized, use:

```bash
python -m pip install -r requirements.txt
```

---

### Step 3 — Run the app

```bash
python -m streamlit run app.py
```

The app will open automatically in your browser at:

```
http://localhost:8501
```

---

## How to Use the App

1. Select the **City** from the dropdown
2. Select the **Property Type** from the dropdown
3. Enter the **Listing Price** in CAD
4. Enter the number of **Bathrooms**
5. Click **Predict Sold Price**
6. The app will display the estimated sold price and whether the property is predicted to sell above or below asking

---

## Model Details

| Item | Detail |
|------|--------|
| Model | Linear Regression |
| Target | `sold_price` (CAD) |
| Dataset | GTA real estate listings (`reduced_dataset.csv`) |
| Features | Listing price, bathrooms, city (OHE), property type (OHE) |
| Scaler | StandardScaler fitted on training data |

---

## Troubleshooting

**`streamlit` is not recognized**
```bash
python -m streamlit run app.py
```

**`pip` is not recognized**
```bash
python -m pip install -r requirements.txt
```

**Model file not found error**
Make sure `model.pkl`, `scaler.pkl`, and `feature_columns.pkl` are in the same folder as `app.py`.

**Port already in use**
```bash
python -m streamlit run app.py --server.port 8502
```

---

## Notes

- This app is for educational purposes only
- Predictions are based on historical GTA listing data
- Model performance: Linear Regression trained on cleaned and feature-engineered dataset
