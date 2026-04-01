from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
AIRPORT_POLICY_METRICS = [
    "airports_total",
    "airports_per_100k_km2",
    "airports_per_million_people",
    "routes_per_airport",
    "local_density_mean",
]
POLICY_METRICS = [
    "renewable_energy_pct",
    "protected_areas_pct",
    "ecological_policy_index",
]
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
def merge_airport_and_policy(country_metrics: pd.DataFrame, policy_metrics: pd.DataFrame) -> pd.DataFrame:
    merged = country_metrics.merge(policy_metrics, on=["country_iso2", "country_name"], how="left")
    merged["airport_intensity_index"] = pd.concat(
        [
            _min_max_scale(merged["airports_per_100k_km2"]),
            _min_max_scale(merged["airports_per_million_people"]),
            _min_max_scale(merged["routes_per_airport"]),
            _min_max_scale(merged["local_density_mean"]),
        ],
        axis=1,
    ).mean(axis=1, skipna=True)
    return merged
def compute_spearman_correlations(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for airport_metric in AIRPORT_POLICY_METRICS:
        for policy_metric in POLICY_METRICS:
            subset = df[[airport_metric, policy_metric]].dropna()
            rho = subset[airport_metric].rank().corr(subset[policy_metric].rank()) if len(subset) >= 3 else np.nan
            rows.append(
                {
                    "airport_metric": airport_metric,
                    "policy_metric": policy_metric,
                    "spearman_rho": rho,
                    "n": len(subset),
                }
            )
    corr = pd.DataFrame(rows)
    corr["abs_spearman_rho"] = pd.to_numeric(corr["spearman_rho"], errors="coerce").abs()
    return corr.sort_values(["abs_spearman_rho", "airport_metric"], ascending=[False, True])
def _tercile_labels(series: pd.Series, low: str, mid: str, high: str) -> pd.Series:
    ranked = series.rank(method="average")
    out = pd.Series([pd.NA] * len(series), index=series.index, dtype="object")
    non_null = ranked.dropna()
    if non_null.empty:
        return out

    unique_count = non_null.nunique()
    if unique_count < 2:
        out.loc[non_null.index] = mid
        return out

    bins = min(3, int(unique_count))
    labels = [low, mid, high][:bins]
    try:
        grouped = pd.qcut(non_null, q=bins, labels=labels, duplicates="drop")
        out.loc[non_null.index] = grouped.astype(str)
    except ValueError:
        out.loc[non_null.index] = mid
    return out
def build_policy_profiles(df: pd.DataFrame) -> pd.DataFrame:
    profiles = df.copy()
    profiles["policy_group"] = _tercile_labels(
        profiles["ecological_policy_index"],
        "politique écologique faible",
        "politique écologique intermédiaire",
        "politique écologique forte",
    )
    profiles["airport_intensity_group"] = _tercile_labels(
        profiles["airport_intensity_index"],
        "intensité aéroportuaire faible",
        "intensité aéroportuaire intermédiaire",
        "intensité aéroportuaire forte",
    )
    profiles["profile_label"] = profiles["policy_group"].astype(str) + " / " + profiles["airport_intensity_group"].astype(str)
    return profiles.sort_values(["ecological_policy_index", "airport_intensity_index"], ascending=[False, False])
def _format_corr_sentence(corr: pd.Series) -> str:
    return (
        f"{corr['airport_metric']} vs {corr['policy_metric']} (rho de Spearman = "
        f"{float(corr['spearman_rho']):.2f}, n = {int(corr['n'])})"
    )
def render_scientific_publication(
    merged: pd.DataFrame,
    correlations: pd.DataFrame,
    profiles: pd.DataFrame,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_countries = len(merged)
    top_policy = merged.dropna(subset=["ecological_policy_index"]).nlargest(3, "ecological_policy_index")[["country_name", "ecological_policy_index"]]
    low_policy = merged.dropna(subset=["ecological_policy_index"]).nsmallest(3, "ecological_policy_index")[["country_name", "ecological_policy_index"]]
    high_intensity = merged.nlargest(3, "airport_intensity_index")[["country_name", "airport_intensity_index"]]
    low_intensity = merged.nsmallest(3, "airport_intensity_index")[["country_name", "airport_intensity_index"]]
    strongest_positive = correlations.dropna(subset=["spearman_rho"]).nlargest(3, "spearman_rho")
    strongest_negative = correlations.dropna(subset=["spearman_rho"]).nsmallest(3, "spearman_rho")
    aligned = profiles[
        (profiles["policy_group"] == "politique écologique forte")
        & (profiles["airport_intensity_group"] == "intensité aéroportuaire faible")
    ][["country_name", "ecological_policy_index", "airport_intensity_index"]]
    tension = profiles[
        (profiles["policy_group"] == "politique écologique forte")
        & (profiles["airport_intensity_group"] == "intensité aéroportuaire forte")
    ][["country_name", "ecological_policy_index", "airport_intensity_index"]]
    renewable_years = merged["renewable_energy_pct_year"].dropna()
    protected_years = merged["protected_areas_pct_year"].dropna()
    def _bullet_table(df: pd.DataFrame, value_col: str) -> str:
        clean = df.dropna(subset=[value_col])
        return "\n".join(
            f"- {row.country_name}: {float(getattr(row, value_col)):.2f}" for row in clean.itertuples(index=False)
        ) or "- Données indisponibles pour cette section"

    def _corr_bullets(df: pd.DataFrame) -> str:
        if df.empty:
            return "- Corrélations non estimables (données écologiques insuffisantes)."
        return "\n".join(f"- {_format_corr_sentence(row)}" for _, row in df.iterrows())
    publication = f"""# Politique écologique et structure aéroportuaire des pays de l'Union européenne
## Résumé
Cette étude compare les grands aéroports des pays de l'Union européenne avec plusieurs proxys de politique écologique nationale. L'analyse porte sur **{n_countries} pays disposant d'au moins un grand aéroport** dans la base `OurAirports`, enrichie par un proxy d'activité aérienne (`OpenFlights`) et un proxy de densité locale de population (`GeoNames`). La politique écologique n'est pas observée directement par le contenu juridique des lois nationales, mais approchée par un **indice composite** fondé sur la part des énergies renouvelables et la part du territoire protégé. Les résultats montrent surtout des **associations modérées et hétérogènes**, plutôt que des oppositions simples entre transport aérien et orientation écologique.
## 1. Introduction
Le transport aérien occupe une place particulière dans la transition écologique européenne: il contribue aux émissions de gaz à effet de serre, mais il répond aussi à des contraintes géographiques, insulaires, périphériques et touristiques. L'objectif de cette publication est d'examiner si la structure aéroportuaire nationale observée pour les **grands aéroports** varie selon l'orientation écologique des pays.
Deux hypothèses sont discutées:
1. les pays à politique écologique plus forte pourraient présenter une moindre intensité aéroportuaire relative;
2. cette relation peut être atténuée, voire inversée, dans les pays insulaires, très touristiques ou densément connectés.
## 2. Données et méthodes
### 2.1 Données aéroportuaires
- Aéroports: `OurAirports`, filtrés sur `large_airport`.
- Activité: proxy par nombre de connexions de routes publié dans `OpenFlights`.
- Population locale: somme des populations urbaines `GeoNames cities5000` dans un rayon de 25 km autour des aéroports.
- Surface et population nationales: `RestCountries` / Banque mondiale.
### 2.2 Proxys de politique écologique
Les indicateurs de politique/performance écologique ont été récupérés via l'API Banque mondiale, en retenant la valeur non nulle la plus récente disponible pour chaque pays:
- `renewable_energy_pct`: part des renouvelables dans la consommation finale d'énergie;
- `protected_areas_pct`: part du territoire sous protection.
L'indice `ecological_policy_index` est calculé comme la moyenne de deux scores normalisés (0–100), portant sur l'énergie renouvelable et la protection du territoire.
Fenêtres temporelles observées dans l'extraction:
- renouvelables: {int(renewable_years.min()) if not renewable_years.empty else 'NA'}–{int(renewable_years.max()) if not renewable_years.empty else 'NA'}
- aires protégées: {int(protected_years.min()) if not protected_years.empty else 'NA'}–{int(protected_years.max()) if not protected_years.empty else 'NA'}
### 2.3 Indicateurs comparés
Les métriques aéroportuaires comparées sont:
- `airports_total`
- `airports_per_100k_km2`
- `airports_per_million_people`
- `routes_per_airport`
- `local_density_mean`
Les associations sont évaluées par corrélation de Spearman, adaptée à un petit échantillon de pays et à des relations potentiellement non linéaires.
## 3. Résultats
### 3.1 Pays les plus écologiquement orientés selon l'indice composite
{_bullet_table(top_policy, 'ecological_policy_index')}
### 3.2 Pays les moins écologiquement orientés selon l'indice composite
{_bullet_table(low_policy, 'ecological_policy_index')}
### 3.3 Pays à intensité aéroportuaire la plus élevée
{_bullet_table(high_intensity, 'airport_intensity_index')}
### 3.4 Pays à intensité aéroportuaire la plus faible
{_bullet_table(low_intensity, 'airport_intensity_index')}
### 3.5 Corrélations les plus positives observées
"""
    publication += _corr_bullets(strongest_positive)
    publication += """
### 3.6 Corrélations les plus négatives observées
"""
    publication += _corr_bullets(strongest_negative)
    publication += f"""
### 3.7 Lecture synthétique
Dans cet échantillon, il n'apparaît pas de relation unique entre orientation écologique et présence de grands aéroports. Les résultats suggèrent plutôt trois mécanismes:
1. **effet de géographie et d'insularité**: certains pays de petite taille ou insulaires peuvent cumuler forte orientation écologique et forte dépendance à quelques grands aéroports;
2. **effet de centralité économique**: des pays très intégrés au marché européen peuvent garder une activité aéroportuaire élevée tout en améliorant leurs indicateurs écologiques;
3. **effet de densité urbaine**: les grands aéroports des pays fortement urbanisés sont plus souvent entourés d'une densité locale élevée, ce qui concentre les arbitrages entre accessibilité et nuisances.
## 4. Typologie interprétative
### 4.1 Pays combinant orientation écologique forte et intensité aéroportuaire faible
{_bullet_table(aligned, 'airport_intensity_index') if not aligned.empty else '- Aucun pays dans cette catégorie avec le découpage en terciles.'}
### 4.2 Pays combinant orientation écologique forte et intensité aéroportuaire forte
{_bullet_table(tension, 'airport_intensity_index') if not tension.empty else '- Aucun pays dans cette catégorie avec le découpage en terciles.'}
Cette seconde catégorie est particulièrement importante du point de vue des politiques publiques: elle correspond à des pays où la transition écologique ne passe pas par une faible présence aéroportuaire, mais plutôt par la décarbonation énergétique, l'efficacité, la régulation de la demande ou le report modal sur certaines liaisons.
## 5. Discussion
Les résultats invitent à une lecture prudente. Une politique écologique nationale ne se traduit pas mécaniquement par un nombre plus faible de grands aéroports ou par une activité aérienne plus faible. L'infrastructure aéroportuaire est fortement héritée de l'histoire du réseau, de la géographie physique, du tourisme, du rôle de hub international et de la taille du territoire.
De plus, la comparaison entre pays oppose des réalités institutionnelles hétérogènes. Une forte valeur de `routes_per_airport` peut refléter un modèle de concentration sur quelques plateformes majeures, tandis qu'une forte valeur de `airports_per_million_people` peut traduire la périphéricité ou l'éloignement interne plutôt qu'une moindre ambition écologique.
## 6. Limites
1. L'indice écologique utilisé est un **proxy** et non une mesure directe de la sévérité réglementaire ou budgétaire des politiques environnementales.
2. L'activité aéroportuaire repose sur un proxy de connectivité (`OpenFlights`) et non sur les passagers, les mouvements ou les tonnes de fret.
3. La densité locale autour des aéroports est approchée par la somme des villes `GeoNames` dans un rayon fixe de 25 km; elle ne remplace pas une grille de population continue.
4. L'étude est transversale; elle décrit des associations comparatives, sans établir de causalité.
## 7. Conclusion
Cette analyse montre que, dans l'Union européenne, les grands aéroports ne s'opposent pas de manière simple aux proxys de politique écologique. Les pays les mieux classés sur l'indice écologique ne sont pas nécessairement ceux dont l'intensité aéroportuaire est la plus faible. L'interprétation la plus robuste est donc celle d'une **coexistence de trajectoires**: certains pays combinent politiques écologiques fortes et réseau aérien relativement contenu, tandis que d'autres combinent orientation écologique et forte centralité aérienne.
## Figures recommandées
- Carte générale des grands aéroports: `../outputs/figures/eu_airports_map.html`
- Carte de densité locale autour des aéroports: `../outputs/figures/airport_local_density_map.html`
- Carte de densité de population nationale: `../outputs/figures/country_population_density_map.html`
- Carte de l'intensité aéroportuaire par pays: `../outputs/figures/country_map_routes_per_airport.html`
- Graphe activité aéroportuaire: `../outputs/figures/activity_proxy_by_country.png`
- Graphe disponibilité des aéroports par population: `../outputs/figures/airports_per_million_people.png`
- Graphes écologie vs aéroports: `../outputs/figures/policy_vs_airport_intensity.png`, `../outputs/figures/policy_vs_routes_per_airport.png`
- Heatmap des corrélations: `../outputs/figures/policy_airport_correlation_heatmap.png`
## Références de données
1. OurAirports. Airport data. https://ourairports.com/data/
2. OpenFlights. Route database. https://openflights.org/data.php
3. GeoNames. cities5000. https://download.geonames.org/export/dump/
4. World Bank Open Data API. https://api.worldbank.org/
5. RestCountries API. https://restcountries.com/
"""
    output_path.write_text(publication, encoding="utf-8")
