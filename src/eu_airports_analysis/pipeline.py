from __future__ import annotations

from pathlib import Path

from .analysis import (
    attach_airport_activity,
    build_country_metrics,
    build_extremes_summary,
    compute_local_population_density_proxy,
)
from .config import FIGURES_DIR, PROCESSED_DIR, REPORTS_DIR, TABLES_DIR
from .data_sources import (
    load_airports,
    load_airports_for_types,
    load_eu_cities,
    load_routes_activity,
    load_worldbank_country_stats,
)
from .ecology_data import load_ecological_policy_proxies
from .policy_analysis import (
    build_policy_profiles,
    compute_spearman_correlations,
    merge_airport_and_policy,
    render_scientific_publication,
)
from .plotting import (
    plot_airports_map,
    plot_airports_map_medium_large_polished,
    plot_country_comparisons,
    plot_country_metric_maps,
    plot_policy_relationships,
    plot_population_density_maps,
)


def run(refresh: bool = False) -> dict[str, Path]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    airports = load_airports(refresh=refresh)
    airports_medium_large = load_airports_for_types(("medium_airport", "large_airport"), refresh=refresh)
    routes = load_routes_activity(refresh=refresh)
    cities = load_eu_cities(refresh=refresh)
    country_stats = load_worldbank_country_stats(refresh=refresh)
    policy_stats = load_ecological_policy_proxies(refresh=refresh)

    airports = attach_airport_activity(airports, routes)
    airports = compute_local_population_density_proxy(airports, cities)
    country_metrics = build_country_metrics(airports, country_stats)
    extremes = build_extremes_summary(country_metrics)
    merged_policy = merge_airport_and_policy(country_metrics, policy_stats)
    policy_correlations = compute_spearman_correlations(merged_policy)
    policy_profiles = build_policy_profiles(merged_policy)

    airports_csv = PROCESSED_DIR / "airports_enriched.csv"
    country_csv = TABLES_DIR / "country_metrics.csv"
    extremes_csv = TABLES_DIR / "extreme_countries_summary.csv"
    ecology_csv = TABLES_DIR / "ecological_policy_country_metrics.csv"
    correlations_csv = TABLES_DIR / "policy_airport_correlations.csv"
    profiles_csv = TABLES_DIR / "policy_country_profiles.csv"
    map_html = FIGURES_DIR / "eu_airports_map.html"
    polished_map_html = FIGURES_DIR / "eu_airports_map_medium_large_polished.html"
    publication_md = REPORTS_DIR / "publication_politique_ecologique_fr.md"

    airports.to_csv(airports_csv, index=False)
    country_metrics.to_csv(country_csv, index=False)
    extremes.to_csv(extremes_csv, index=False)
    merged_policy.to_csv(ecology_csv, index=False)
    policy_correlations.to_csv(correlations_csv, index=False)
    policy_profiles.to_csv(profiles_csv, index=False)

    plot_airports_map(airports, map_html)
    plot_airports_map_medium_large_polished(airports_medium_large, polished_map_html)
    plot_country_comparisons(country_metrics, airports, FIGURES_DIR)
    country_maps = plot_country_metric_maps(country_metrics, FIGURES_DIR)
    density_maps = plot_population_density_maps(airports, cities, country_metrics, FIGURES_DIR)
    policy_figures = plot_policy_relationships(merged_policy, policy_correlations, FIGURES_DIR)
    render_scientific_publication(merged_policy, policy_correlations, policy_profiles, publication_md)

    outputs = {
        "airports": airports_csv,
        "country_metrics": country_csv,
        "extremes": extremes_csv,
        "ecological_policy_metrics": ecology_csv,
        "policy_correlations": correlations_csv,
        "policy_profiles": profiles_csv,
        "map": map_html,
        "map_medium_large_polished": polished_map_html,
        "publication": publication_md,
    }
    for idx, path in enumerate(country_maps, start=1):
        outputs[f"country_map_{idx}"] = path
    outputs.update(density_maps)
    outputs.update(policy_figures)
    return outputs
