from __future__ import annotations

import io
import zipfile

import pandas as pd
import requests

from .config import (
    AIRPORT_TYPES_FILTER,
    EU_COUNTRIES,
    GEONAMES_CITIES5000_URL,
    OPENFLIGHTS_ROUTES_URL,
    OURAIRPORTS_URL,
    RAW_DIR,
    RESTCOUNTRIES_URL,
    WORLDBANK_API,
)


def _download_text(url: str, timeout: int = 60) -> str:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def _download_bytes(url: str, timeout: int = 60) -> bytes:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.content


def load_airports(refresh: bool = False) -> pd.DataFrame:
    return load_airports_for_types(AIRPORT_TYPES_FILTER, refresh=refresh)


def load_airports_for_types(airport_types: tuple[str, ...], refresh: bool = False) -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache = RAW_DIR / "ourairports_airports.csv"
    if refresh or not cache.exists():
        cache.write_text(_download_text(OURAIRPORTS_URL), encoding="utf-8")
    airports = pd.read_csv(cache)
    airports = airports[
        airports["iso_country"].isin(EU_COUNTRIES.keys())
        & airports["type"].isin(airport_types)
    ].copy()
    airports = airports[["ident", "name", "type", "iso_country", "iata_code", "latitude_deg", "longitude_deg"]]
    airports.rename(
        columns={
            "ident": "icao",
            "iso_country": "country_iso2",
            "latitude_deg": "lat",
            "longitude_deg": "lon",
        },
        inplace=True,
    )
    airports["country_name"] = airports["country_iso2"].map(EU_COUNTRIES)
    return airports


def load_routes_activity(refresh: bool = False) -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache = RAW_DIR / "openflights_routes.dat"
    if refresh or not cache.exists():
        cache.write_text(_download_text(OPENFLIGHTS_ROUTES_URL), encoding="utf-8")

    columns = [
        "airline",
        "airline_id",
        "source_airport",
        "source_airport_id",
        "destination_airport",
        "destination_airport_id",
        "codeshare",
        "stops",
        "equipment",
    ]
    routes = pd.read_csv(cache, names=columns, header=None)

    source_counts = routes.groupby("source_airport").size().rename("source_routes")
    dest_counts = routes.groupby("destination_airport").size().rename("destination_routes")
    activity = pd.concat([source_counts, dest_counts], axis=1).fillna(0)
    activity["route_connections"] = activity["source_routes"] + activity["destination_routes"]
    activity.reset_index(inplace=True)
    activity.rename(columns={"index": "iata_code"}, inplace=True)
    return activity[["iata_code", "route_connections"]]


def _load_country_stats_from_restcountries() -> pd.DataFrame:
    response = requests.get(RESTCOUNTRIES_URL, timeout=90)
    response.raise_for_status()
    payload = response.json()

    rows = []
    for item in payload:
        iso2 = item.get("cca2")
        if iso2 not in EU_COUNTRIES:
            continue
        rows.append(
            {
                "country_iso2": iso2,
                "country_name": EU_COUNTRIES[iso2],
                "population": item.get("population"),
                "surface_km2": item.get("area"),
            }
        )
    return pd.DataFrame(rows)


def _load_country_stats_from_worldbank() -> pd.DataFrame:
    rows = []
    indicators = {
        "SP.POP.TOTL": "population",
        "AG.LND.TOTL.K2": "surface_km2",
    }
    for iso2, name in EU_COUNTRIES.items():
        item = {"country_iso2": iso2, "country_name": name}
        for indicator, column in indicators.items():
            value = None
            url = WORLDBANK_API.format(iso2=iso2.lower(), indicator=indicator)
            try:
                data = requests.get(url, timeout=60)
                data.raise_for_status()
                payload = data.json()
                if isinstance(payload, list) and len(payload) > 1:
                    for rec in payload[1]:
                        if rec.get("value") is not None:
                            value = rec["value"]
                            break
            except requests.RequestException:
                value = None
            item[column] = value
        rows.append(item)
    return pd.DataFrame(rows)


def load_worldbank_country_stats(refresh: bool = False) -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache = RAW_DIR / "country_stats.csv"

    if refresh or not cache.exists():
        stats = pd.DataFrame()
        try:
            stats = _load_country_stats_from_restcountries()
        except requests.RequestException:
            stats = pd.DataFrame()

        if stats.empty:
            stats = _load_country_stats_from_worldbank()

        stats.to_csv(cache, index=False)

    return pd.read_csv(cache)


def load_eu_cities(refresh: bool = False) -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache = RAW_DIR / "geonames_cities5000_eu.csv"
    if refresh or not cache.exists():
        zip_bytes = _download_bytes(GEONAMES_CITIES5000_URL, timeout=120)
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            with zf.open("cities5000.txt") as txt:
                columns = [
                    "geonameid",
                    "name",
                    "asciiname",
                    "alternatenames",
                    "lat",
                    "lon",
                    "feature_class",
                    "feature_code",
                    "country_iso2",
                    "cc2",
                    "admin1",
                    "admin2",
                    "admin3",
                    "admin4",
                    "population",
                    "elevation",
                    "dem",
                    "timezone",
                    "modification_date",
                ]
                cities = pd.read_csv(txt, sep="\t", header=None, names=columns, low_memory=False)
        cities = cities[cities["country_iso2"].isin(EU_COUNTRIES.keys())].copy()
        cities = cities[["name", "country_iso2", "lat", "lon", "population"]]
        cities = cities[cities["population"] > 0]
        cities.to_csv(cache, index=False)

    return pd.read_csv(cache)
