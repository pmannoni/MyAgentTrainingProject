from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .config import POP_RADIUS_KM


def haversine_km(lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    earth_radius_km = 6371.0
    d_lat = np.radians(lat2 - lat1)
    d_lon = np.radians(lon2 - lon1)
    a = (
        np.sin(d_lat / 2.0) ** 2
        + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(d_lon / 2.0) ** 2
    )
    return 2.0 * earth_radius_km * np.arcsin(np.sqrt(a))


def attach_airport_activity(airports: pd.DataFrame, route_activity: pd.DataFrame) -> pd.DataFrame:
    merged = airports.merge(route_activity, on="iata_code", how="left")
    merged["route_connections"] = merged["route_connections"].fillna(0)
    return merged


def compute_local_population_density_proxy(
    airports: pd.DataFrame,
    cities: pd.DataFrame,
    radius_km: float = POP_RADIUS_KM,
) -> pd.DataFrame:
    radius_area = math.pi * radius_km * radius_km
    output = airports.copy()
    nearby_population = []

    for row in output.itertuples(index=False):
        city_pool = cities[cities["country_iso2"] == row.country_iso2]
        if city_pool.empty:
            nearby_population.append(0.0)
            continue

        lat2 = city_pool["lat"].to_numpy(dtype=float)
        lon2 = city_pool["lon"].to_numpy(dtype=float)
        dist = haversine_km(np.full_like(lat2, row.lat, dtype=float), np.full_like(lon2, row.lon, dtype=float), lat2, lon2)
        pop = city_pool["population"].to_numpy(dtype=float)
        nearby_population.append(pop[dist <= radius_km].sum())

    output["nearby_population_25km"] = nearby_population
    output["local_density_proxy_pop_per_km2"] = output["nearby_population_25km"] / radius_area
    return output


def build_country_metrics(airports_enriched: pd.DataFrame, country_stats: pd.DataFrame) -> pd.DataFrame:
    grouped = airports_enriched.groupby(["country_iso2", "country_name"], as_index=False).agg(
        airports_total=("icao", "count"),
        airports_large=("type", lambda s: (s == "large_airport").sum()),
        airports_medium=("type", lambda s: (s == "medium_airport").sum()),
        routes_total=("route_connections", "sum"),
        routes_mean=("route_connections", "mean"),
        local_density_mean=("local_density_proxy_pop_per_km2", "mean"),
        local_density_median=("local_density_proxy_pop_per_km2", "median"),
    )

    out = grouped.merge(country_stats, on=["country_iso2", "country_name"], how="left")
    out["airports_per_100k_km2"] = (out["airports_total"] / out["surface_km2"]) * 100000.0
    out["airports_per_million_people"] = (out["airports_total"] / out["population"]) * 1_000_000.0
    out["routes_per_airport"] = out["routes_total"] / out["airports_total"]
    out["population_density_country"] = out["population"] / out["surface_km2"]
    return out.sort_values("airports_total", ascending=False)


def build_extremes_summary(country_metrics: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "airports_total",
        "airports_per_100k_km2",
        "airports_per_million_people",
        "routes_per_airport",
        "local_density_mean",
        "population_density_country",
    ]
    rows = []
    for metric in metrics:
        valid = country_metrics.dropna(subset=[metric])
        top = valid.nlargest(1, metric).iloc[0]
        low = valid.nsmallest(1, metric).iloc[0]
        rows.append({"metric": metric, "extreme": "highest", "country": top["country_name"], "value": top[metric]})
        rows.append({"metric": metric, "extreme": "lowest", "country": low["country_name"], "value": low[metric]})
    return pd.DataFrame(rows)

