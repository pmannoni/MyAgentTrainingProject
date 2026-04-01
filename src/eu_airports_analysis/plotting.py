from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .config import COUNTRY_MAP_METRICS


def plot_airports_map(airports: pd.DataFrame, output_file: Path) -> None:
    fig = px.scatter_geo(
        airports,
        lat="lat",
        lon="lon",
        color="route_connections",
        size="route_connections",
        hover_name="name",
        hover_data={"country_name": True, "iata_code": True, "route_connections": True},
        scope="europe",
        title="EU large airports (size/color = route connectivity proxy)",
        projection="natural earth",
        color_continuous_scale="Viridis",
    )
    fig.write_html(str(output_file), include_plotlyjs="cdn")


def plot_country_comparisons(country_metrics: pd.DataFrame, airports: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(country_metrics["surface_km2"], country_metrics["airports_total"])
    for row in country_metrics.itertuples(index=False):
        ax.annotate(row.country_iso2, (row.surface_km2, row.airports_total), fontsize=8)
    ax.set_xlabel("Surface area (km2)")
    ax.set_ylabel("Number of large airports")
    ax.set_title("Large airports vs country surface area")
    fig.tight_layout()
    fig.savefig(output_dir / "airports_vs_surface.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(country_metrics["population"], country_metrics["airports_total"])
    for row in country_metrics.itertuples(index=False):
        ax.annotate(row.country_iso2, (row.population, row.airports_total), fontsize=8)
    ax.set_xlabel("Population")
    ax.set_ylabel("Number of large airports")
    ax.set_title("Large airports vs country population")
    fig.tight_layout()
    fig.savefig(output_dir / "airports_vs_population.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 6))
    ordered = country_metrics.sort_values("routes_per_airport", ascending=False)
    ax.bar(ordered["country_iso2"], ordered["routes_per_airport"])
    ax.set_xlabel("Country")
    ax.set_ylabel("Route connections per airport")
    ax.set_title("Large-airport activity proxy by country")
    ax.tick_params(axis="x", labelrotation=75)
    fig.tight_layout()
    fig.savefig(output_dir / "activity_proxy_by_country.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 6))
    ordered = country_metrics.sort_values("local_density_mean", ascending=False)
    ax.bar(ordered["country_iso2"], ordered["local_density_mean"])
    ax.set_xlabel("Country")
    ax.set_ylabel("Mean nearby population density proxy")
    ax.set_title("Large-airport surroundings: nearby population density proxy")
    ax.tick_params(axis="x", labelrotation=75)
    fig.tight_layout()
    fig.savefig(output_dir / "nearby_density_proxy_by_country.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 6))
    ordered = country_metrics.sort_values("airports_per_million_people", ascending=False)
    ax.bar(ordered["country_iso2"], ordered["airports_per_million_people"])
    ax.set_xlabel("Country")
    ax.set_ylabel("Large airports per million people")
    ax.set_title("Large-airport availability per population")
    ax.tick_params(axis="x", labelrotation=75)
    fig.tight_layout()
    fig.savefig(output_dir / "airports_per_million_people.png", dpi=180)
    plt.close(fig)

    top_countries = country_metrics.nlargest(10, "airports_total")["country_iso2"].tolist()
    subset = airports[airports["country_iso2"].isin(top_countries)]
    fig, ax = plt.subplots(figsize=(11, 6))
    groups = [subset.loc[subset["country_iso2"] == code, "route_connections"].to_numpy() for code in top_countries]
    ax.boxplot(groups, labels=top_countries, showfliers=False)
    ax.set_xlabel("Country (top 10 by large airport count)")
    ax.set_ylabel("Route connections per airport")
    ax.set_title("Distribution of airport activity proxy")
    ax.tick_params(axis="x", labelrotation=75)
    fig.tight_layout()
    fig.savefig(output_dir / "route_connections_distribution_top10.png", dpi=180)
    plt.close(fig)


def plot_country_metric_maps(country_metrics: pd.DataFrame, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []

    for metric in COUNTRY_MAP_METRICS:
        metric_df = country_metrics.dropna(subset=[metric]).copy()
        fig = px.choropleth(
            metric_df,
            locations="country_iso2",
            color=metric,
            hover_name="country_name",
            scope="europe",
            color_continuous_scale="Plasma",
            title=f"EU countries - {metric}",
        )
        out = output_dir / f"country_map_{metric}.html"
        fig.write_html(str(out), include_plotlyjs="cdn")
        outputs.append(out)

    return outputs


def plot_population_density_maps(
    airports: pd.DataFrame,
    cities: pd.DataFrame,
    country_metrics: pd.DataFrame,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    cities = cities.copy()
    cities["city_pop_log10"] = np.log10(cities["population"].clip(lower=1))
    city_map = px.scatter_geo(
        cities,
        lat="lat",
        lon="lon",
        color="city_pop_log10",
        size="population",
        hover_name="name",
        hover_data={"country_iso2": True, "population": True},
        scope="europe",
        projection="natural earth",
        title="EU city population concentration (GeoNames cities5000 proxy)",
        color_continuous_scale="Turbo",
        size_max=14,
    )
    city_map_file = output_dir / "population_density_cities_map.html"
    city_map.write_html(str(city_map_file), include_plotlyjs="cdn")

    airport_density_map = px.scatter_geo(
        airports,
        lat="lat",
        lon="lon",
        color="local_density_proxy_pop_per_km2",
        size="nearby_population_25km",
        hover_name="name",
        hover_data={
            "country_name": True,
            "nearby_population_25km": ":,.0f",
            "local_density_proxy_pop_per_km2": ":.2f",
        },
        scope="europe",
        projection="natural earth",
        title="Large airports and nearby population density proxy (25 km)",
        color_continuous_scale="Inferno",
        size_max=18,
    )
    airport_density_file = output_dir / "airport_local_density_map.html"
    airport_density_map.write_html(str(airport_density_file), include_plotlyjs="cdn")

    country_density_map = px.choropleth(
        country_metrics.dropna(subset=["population_density_country"]),
        locations="country_iso2",
        color="population_density_country",
        hover_name="country_name",
        scope="europe",
        color_continuous_scale="Viridis",
        title="EU country population density (people per km2)",
    )
    country_density_file = output_dir / "country_population_density_map.html"
    country_density_map.write_html(str(country_density_file), include_plotlyjs="cdn")

    return {
        "cities_density": city_map_file,
        "airport_local_density": airport_density_file,
        "country_population_density": country_density_file,
    }


def plot_policy_relationships(
    merged_metrics: pd.DataFrame,
    correlations: pd.DataFrame,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(merged_metrics["ecological_policy_index"], merged_metrics["airport_intensity_index"])
    for row in merged_metrics.itertuples(index=False):
        ax.annotate(row.country_iso2, (row.ecological_policy_index, row.airport_intensity_index), fontsize=8)
    ax.set_xlabel("Ecological policy index (proxy)")
    ax.set_ylabel("Airport intensity index")
    ax.set_title("Ecological policy orientation vs airport intensity")
    fig.tight_layout()
    policy_intensity = output_dir / "policy_vs_airport_intensity.png"
    fig.savefig(policy_intensity, dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(merged_metrics["ecological_policy_index"], merged_metrics["routes_per_airport"])
    for row in merged_metrics.itertuples(index=False):
        ax.annotate(row.country_iso2, (row.ecological_policy_index, row.routes_per_airport), fontsize=8)
    ax.set_xlabel("Ecological policy index (proxy)")
    ax.set_ylabel("Route connections per airport")
    ax.set_title("Ecological policy orientation vs airport activity proxy")
    fig.tight_layout()
    policy_routes = output_dir / "policy_vs_routes_per_airport.png"
    fig.savefig(policy_routes, dpi=180)
    plt.close(fig)

    pivot = correlations.pivot(index="airport_metric", columns="policy_metric", values="spearman_rho")
    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(pivot.to_numpy(dtype=float), cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(pivot.columns)), labels=pivot.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(pivot.index)), labels=pivot.index)
    ax.set_title("Spearman correlations: airport metrics vs ecological policy proxies")
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            if pd.notna(value):
                ax.text(j, i, f"{value:.2f}", ha="center", va="center", color="black", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    heatmap = output_dir / "policy_airport_correlation_heatmap.png"
    fig.savefig(heatmap, dpi=180)
    plt.close(fig)

    return {
        "policy_vs_airport_intensity": policy_intensity,
        "policy_vs_routes_per_airport": policy_routes,
        "policy_airport_correlation_heatmap": heatmap,
    }


def plot_airports_map_medium_large_polished(airports: pd.DataFrame, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    type_labels = {
        "large_airport": "Grand aeroport",
        "medium_airport": "Aeroport moyen",
    }
    colors = {
        "large_airport": "#e63946",
        "medium_airport": "#1d3557",
    }
    sizes = {
        "large_airport": 10,
        "medium_airport": 7,
    }

    fig = go.Figure()
    for airport_type in ["large_airport", "medium_airport"]:
        subset = airports[airports["type"] == airport_type]
        if subset.empty:
            continue
        fig.add_trace(
            go.Scattergeo(
                lon=subset["lon"],
                lat=subset["lat"],
                text=subset["name"],
                customdata=np.stack(
                    [
                        subset["country_name"].fillna(""),
                        subset["iata_code"].fillna(""),
                        subset["type"].map(type_labels).fillna(subset["type"]),
                    ],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Pays: %{customdata[0]}<br>"
                    "Type: %{customdata[2]}<br>"
                    "IATA: %{customdata[1]}<extra></extra>"
                ),
                mode="markers",
                marker={
                    "size": sizes[airport_type],
                    "color": colors[airport_type],
                    "line": {"color": "white", "width": 0.8},
                    "opacity": 0.82,
                },
                name=type_labels[airport_type],
            )
        )

    fig.update_geos(
        scope="europe",
        projection_type="natural earth",
        showcoastlines=True,
        coastlinecolor="#6c757d",
        showcountries=True,
        countrycolor="#adb5bd",
        showland=True,
        landcolor="#f8f9fa",
        showocean=True,
        oceancolor="#edf2fb",
        lataxis_range=[34, 72],
        lonaxis_range=[-26, 45],
    )
    fig.update_layout(
        title={
            "text": "Aeroports moyens et grands en Europe (UE)",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 23},
        },
        template="plotly_white",
        margin={"l": 10, "r": 10, "t": 70, "b": 10},
        legend={
            "title": {"text": "Type d'aeroport"},
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": 0.02,
            "yanchor": "bottom",
            "bgcolor": "rgba(255,255,255,0.85)",
            "bordercolor": "#dee2e6",
            "borderwidth": 1,
        },
        annotations=[
            {
                "text": "Source: OurAirports | Filtre: medium_airport + large_airport",
                "xref": "paper",
                "yref": "paper",
                "x": 0.99,
                "y": 0.0,
                "showarrow": False,
                "font": {"size": 11, "color": "#6c757d"},
            }
        ],
    )
    fig.write_html(str(output_file), include_plotlyjs="cdn")


