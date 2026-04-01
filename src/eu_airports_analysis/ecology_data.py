from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
import requests

from .config import EU_COUNTRIES, RAW_DIR

WORLD_BANK_BULK_API = (
    "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}?format=json&per_page=4000"
)
POLICY_INDICATORS = {
    "EG.FEC.RNEW.ZS": "renewable_energy_pct",
    "ER.LND.PTLD.ZS": "protected_areas_pct",
}


def _min_max_scale(series: pd.Series, *, inverse: bool = False) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    valid = values.dropna()
    if valid.empty:
        return pd.Series([np.nan] * len(series), index=series.index, dtype="float64")
    if valid.max() == valid.min():
        scaled = pd.Series([50.0] * len(series), index=series.index, dtype="float64")
    else:
        scaled = (values - valid.min()) / (valid.max() - valid.min())
        scaled = scaled * 100.0
    if inverse:
        scaled = 100.0 - scaled
    return scaled


def _empty_indicator_frame(column_name: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "country_iso2": iso2,
                "country_name": country_name,
                column_name: pd.NA,
                f"{column_name}_year": pd.NA,
            }
            for iso2, country_name in EU_COUNTRIES.items()
        ]
    )


def _fetch_indicator_records(indicator: str, countries: Iterable[str]) -> list[dict]:
    records: list[dict] = []
    country_list = sorted(countries)
    for start in range(0, len(country_list), 8):
        chunk = country_list[start : start + 8]
        joined = ";".join(chunk)
        url = WORLD_BANK_BULK_API.format(countries=joined, indicator=indicator)
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, list) and len(payload) >= 2:
                records.extend(payload[1])
        except requests.RequestException:
            # Keep whatever records were already collected from other chunks.
            continue
    return records


def _latest_values_for_indicator(indicator: str, column_name: str) -> pd.DataFrame:
    records = _fetch_indicator_records(indicator, EU_COUNTRIES.keys())
    rows = []
    for country_iso2, country_name in EU_COUNTRIES.items():
        country_records = [
            rec
            for rec in records
            if rec.get("country", {}).get("id") == country_iso2 and rec.get("value") is not None and rec.get("date")
        ]
        if country_records:
            country_records.sort(key=lambda rec: int(rec["date"]), reverse=True)
            best = country_records[0]
            rows.append(
                {
                    "country_iso2": country_iso2,
                    "country_name": country_name,
                    column_name: best["value"],
                    f"{column_name}_year": int(best["date"]),
                }
            )
        else:
            rows.append(
                {
                    "country_iso2": country_iso2,
                    "country_name": country_name,
                    column_name: pd.NA,
                    f"{column_name}_year": pd.NA,
                }
            )
    return pd.DataFrame(rows)


def load_ecological_policy_proxies(refresh: bool = False) -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache = RAW_DIR / "ecological_policy_proxies.csv"

    if refresh or not cache.exists():
        frames = []
        for indicator, column_name in POLICY_INDICATORS.items():
            try:
                frames.append(_latest_values_for_indicator(indicator, column_name))
            except requests.RequestException:
                # Keep pipeline runnable even if an indicator endpoint is temporarily unavailable.
                frames.append(_empty_indicator_frame(column_name))

        policy = frames[0]
        for frame in frames[1:]:
            policy = policy.merge(frame, on=["country_iso2", "country_name"], how="outer")

        policy["renewable_score"] = _min_max_scale(policy["renewable_energy_pct"])
        policy["protected_areas_score"] = _min_max_scale(policy["protected_areas_pct"])
        policy["ecological_policy_index"] = policy[["renewable_score", "protected_areas_score"]].mean(axis=1, skipna=True)
        policy.to_csv(cache, index=False)

    return pd.read_csv(cache)
