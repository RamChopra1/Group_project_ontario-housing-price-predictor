# 01 — Data Collection: Redfin Canada Sold Listings (RapidAPI)

**File:** `01_data_collection_rapidapi_redfin_sold.ipynb`  
**Author:** Data Collection Team  
**Date:** April 13, 2026  
**Output:** `redfin_sold_listings_CLEANED_04132026.csv`

---

## Overview

This notebook scrapes sold residential property listings across the Greater Toronto Area (GTA) using the [Redfin Canada API via RapidAPI](https://rapidapi.com/). It covers 29 GTA cities and municipalities, retrieves sold listings paginated up to 10 pages per region, saves raw JSON responses to disk, loads and consolidates them into a single DataFrame, cleans and filters the data, and exports a final CSV ready for the EDA and preprocessing pipeline.

---

## Dependencies

```bash
pip install pandas numpy httpx requests
```

| Package | Purpose |
|---------|---------|
| `pandas` | DataFrame operations and CSV export |
| `numpy` | Numeric coercion helpers |
| `httpx` | Async-capable HTTP client used for paginated API calls |
| `requests` | Used for the autocomplete lookup |
| `json` | JSON serialization for raw response saving |
| `pathlib` | File path management for output directories |
| `os` | Reading environment variables for API key |

---

## API Authentication

The scraper requires a RapidAPI key set as an environment variable. Never hardcode the key in the notebook.

```bash
# Set in your terminal or .env file
export RAPIDAPI_KEY=your_key_here
```

```python
# Used in headers as:
"x-rapidapi-key": os.getenv('RAPIDAPI_KEY')
```

**API Host:** `redfin-canada.p.rapidapi.com`  
**Subscription required at:** https://rapidapi.com/

---

## Core Function — `get_sold_listings`

```python
get_sold_listings(region_id, sold_within, url=url, headers=headers, max_pages=10)
```

Fetches paginated sold listings for a single region from the Redfin Canada API and saves each page's response to disk as JSON.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `region_id` | `str` | Redfin region ID for the target city (e.g. `'33_2775'` for Mississauga) |
| `sold_within` | `int` | Number of days back to search for sold listings (e.g. `365` for the past year) |
| `url` | `str` | API endpoint URL (default: `search-sold` endpoint) |
| `headers` | `dict` | Request headers including the RapidAPI key |
| `max_pages` | `int` | Maximum number of pages to fetch per region (default: `10`, API limit: 1000 results per page) |

### Returns

`list` — a flat list of listing dictionaries from all pages fetched for that region. Returns an empty list if the API returns a non-200 status.

### Output Files

For each region, two JSON files are saved per page under:
```
../redfin/data_04132026/{region_id}/
    redfin-listings_results_sold_price_{page}.json   ← listing rows only
    redfin-listings_full_sold_price_{page}.json      ← full API response including metadata
```

Pagination stops automatically when either `max_pages` is reached or the API's `meta.totalPage` value is hit.

### Usage

```python
# Single region
sold_listings = get_sold_listings(region_id='33_2775', sold_within=365)

# All regions in the mapping
listings = []
for id in region_mapping.values():
    sold_listings = get_sold_listings(id, 365)
    if sold_listings:
        listings.append(sold_listings)
```

---

## Region Mapping

The `region_mapping` dictionary maps city/municipality names to Redfin region IDs. The `gta_cities` list defines the full set of GTA municipalities covered by the project.

**29 regions covered:**

| Region | ID |
|--------|----|
| Toronto | `33_1513` |
| Mississauga | `33_2775` |
| Brampton | `33_3446` |
| Vaughan | `33_2977` |
| Markham | `33_2035` |
| Richmond Hill | `33_2137` |
| Oshawa | `33_2386` |
| Whitby | `33_3469` |
| Ajax | `33_3402` |
| Pickering | `33_3011` |
| Burlington | `33_2828` |
| Halton Hills | `33_2999` |
| Aurora | `33_3451` |
| Newmarket | `33_552186` |
| Caledon | `33_3124` |
| Clarington | `33_3012` |
| Scugog | `33_1555` |
| Uxbridge | `33_2975` |
| Whitchurch-Stouffville | `33_3476` |
| King | `33_3399` |
| East Gwillimbury | `33_2143` |
| Brock | `33_2976` |
| Durham Region | `33_1512` |
| Peel Region | `33_1514` |
| York Region | `33_1513` |
| Mono | `33_2401` |
| Orangeville | `33_3457` |
| New Tecumseth | `33_3524` |
| Georgetown | `33_546831` |

---

## Helper Function — `load_json_file`

```python
load_json_file(path)
```

Loads a single JSON file from disk and normalises it into a flat pandas DataFrame using `pd.json_normalize` with `_` as the separator for nested keys.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `Path` | Full file path to the JSON file |

### Returns

`pd.DataFrame` — normalised flat DataFrame from the JSON payload. Handles both list-type and dict-type JSON roots.

### Usage

```python
DIR_PATH = Path(os.getcwd()).parent / "redfin" / "data_04132026"
listings_json = sorted(DIR_PATH.rglob("*_results_*.json"))

all_dfs = []
for result in listings_json:
    df_result = load_json_file(result)
    df_result["source_file"] = str(result.relative_to(DIR_PATH))
    all_dfs.append(df_result)

all_df = pd.concat(all_dfs, ignore_index=True, sort=False)
```

---

## Cleaning Pipeline

After loading all JSON files into one DataFrame, the following cleaning steps are applied in sequence:

| Step | Action |
|------|--------|
| **1. Deduplicate** | Drop duplicate rows based on `homeData_propertyId`, `propertyId`, or `listingId` (whichever is available) |
| **2. Numeric coercion** | Convert `sold_price`, `homeData_beds`, `homeData_bathInfo_computedFullBaths`, `homeData_sqftInfo_amount`, `latitude`, `longitude` to numeric using `pd.to_numeric(errors='coerce')` |
| **3. Text cleanup** | Strip whitespace from city, state, postal code; uppercase state values |
| **4. Validity filters** | Remove rows where `sold_price <= 0`; remove rows with invalid lat/lon coordinates outside ±90/±180 bounds |
| **5. Drop sparse columns** | Drop any column with more than 95% null values |
| **6. Ontario filter** | Keep only rows where `homeData_addressInfo_state == 'ON'` |
| **7. sold_price** | Assign `homeData_priceInfo_amount` as the `sold_price` column |
| **8. Temporal features** | Parse `homeData_lastSaleData_lastSoldDate` into `sold_date_dt`; compute `days_since_sold` from UTC now; clip negative values to 0 |
| **9. Fill nulls** | Fill `homeData_addressInfo_unitNumber` → `0`; `homeData_hoaDues_amount` → `0.0`; `homeData_lotSize_amount` → `0.0`; `homeData_listingMetadata_hasVirtualTour` → `False` |
| **10. Drop columns** | Remove ~35 redundant or PII columns (broker/agent names, raw bath counts, internal metadata fields) |

---

## Output

**File:** `redfin_sold_listings_CLEANED_04132026.csv`  
**Location:** Current working directory  
**Contents:** One row per unique sold listing in Ontario, with all `homeData_*` fields normalised to flat columns.

This file feeds into the merge step that produces the dataset used by `02_eda.ipynb` and the downstream preprocessing pipeline.

---

## Notes

- The `sold_within` parameter of `365` captures listings sold in the past year from the date the scraper is run — re-running on a different date will produce a different dataset
- The `autocomplete` endpoint (Cell 2) is used to look up region IDs interactively — it is not part of the main collection loop
- Raw JSON files are preserved on disk under `../redfin/data_04132026/` so the collection step does not need to be re-run if the cleaning logic changes
- The column inspection loop in Cell 22 prints unique values for all categorical columns — columns with fewer than 10 unique values are highlighted in red for review
