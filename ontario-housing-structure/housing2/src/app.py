import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GTA Home Price Predictor",
    page_icon="🏠",
    layout="centered"
)

# ── Load model artifacts ────────────────────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    model           = joblib.load('model.pkl')
    scaler          = joblib.load('scaler.pkl')
    feature_columns = joblib.load('feature_columns.pkl')
    return model, scaler, feature_columns

model, scaler, feature_columns = load_artifacts()

# ── Derive city and property_type options from feature columns ──────────────────
cities = sorted([
    col.replace('city_', '')
    for col in feature_columns
    if col.startswith('city_')
])

property_types = sorted([
    col.replace('property_type_', '')
    for col in feature_columns
    if col.startswith('property_type_')
])

# ── UI ─────────────────────────────────────────────────────────────────────────
st.title("🏠 GTA Home Price Predictor")
st.markdown("Enter the property details below to get an estimated sold price.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    city = st.selectbox(
        "City",
        options=["(Other)"] + cities,
        help="Select the city the property is located in"
    )

    listing_price = st.number_input(
        "Listing Price (CAD $)",
        min_value=50_000,
        max_value=15_000_000,
        value=800_000,
        step=5_000,
        format="%d"
    )

with col2:
    property_type = st.selectbox(
        "Property Type",
        options=["(Other)"] + property_types,
        help="Select the property type"
    )

    bathrooms = st.number_input(
        "Bathrooms",
        min_value=1,
        max_value=10,
        value=2,
        step=1
    )

st.divider()

# ── Predict ─────────────────────────────────────────────────────────────────────
def build_input(city, property_type, listing_price, bathrooms):
    """Build a single-row DataFrame matching the model's feature columns."""
    row = {col: 0 for col in feature_columns}

    # Numeric features
    if 'listing_price' in row:
        row['listing_price'] = listing_price
    if 'bathrooms' in row:
        row['bathrooms'] = bathrooms

    # OHE — city
    city_col = f'city_{city}'
    if city_col in row:
        row[city_col] = 1

    # OHE — property_type
    prop_col = f'property_type_{property_type}'
    if prop_col in row:
        row[prop_col] = 1

    return pd.DataFrame([row])[feature_columns]

if st.button("Predict Sold Price", type="primary", use_container_width=True):
    input_df  = build_input(city, property_type, listing_price, bathrooms)
    input_scaled = scaler.transform(input_df)
    prediction   = model.predict(input_scaled)[0]

    st.success(f"### Estimated Sold Price: **${prediction:,.0f} CAD**")

    # ── Breakdown ──────────────────────────────────────────────────────────────
    with st.expander("See input summary"):
        st.write({
            "City"           : city,
            "Property Type"  : property_type,
            "Listing Price"  : f"${listing_price:,}",
            "Bathrooms"      : bathrooms,
        })

    diff = prediction - listing_price
    diff_pct = (diff / listing_price) * 100
    if diff > 0:
        st.info(f"📈 Predicted to sell **${diff:,.0f} above** asking ({diff_pct:.1f}%)")
    elif diff < 0:
        st.info(f"📉 Predicted to sell **${abs(diff):,.0f} below** asking ({diff_pct:.1f}%)")
    else:
        st.info("Predicted to sell at exactly asking price.")

st.divider()
st.caption("Model: Linear Regression trained on GTA real estate listings | For educational purposes only")
