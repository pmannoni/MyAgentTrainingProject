# Politique écologique et structure aéroportuaire des pays de l'Union européenne
## Résumé
Cette étude compare les grands aéroports des pays de l'Union européenne avec plusieurs proxys de politique écologique nationale. L'analyse porte sur **27 pays disposant d'au moins un grand aéroport** dans la base `OurAirports`, enrichie par un proxy d'activité aérienne (`OpenFlights`) et un proxy de densité locale de population (`GeoNames`). La politique écologique n'est pas observée directement par le contenu juridique des lois nationales, mais approchée par un **indice composite** fondé sur la part des énergies renouvelables et la part du territoire protégé. Les résultats montrent surtout des **associations modérées et hétérogènes**, plutôt que des oppositions simples entre transport aérien et orientation écologique.
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
- renouvelables: 2021–2021
- aires protégées: 2024–2024
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
- Croatia: 66.25
- Bulgaria: 61.97
- Slovenia: 58.82
### 3.2 Pays les moins écologiquement orientés selon l'indice composite
- Ireland: 5.46
- Belgium: 7.54
- Netherlands: 18.80
### 3.3 Pays à intensité aéroportuaire la plus élevée
- Malta: 69.02
- France: 42.83
- Belgium: 42.48
### 3.4 Pays à intensité aéroportuaire la plus faible
- Slovakia: 8.81
- Slovenia: 9.96
- Bulgaria: 11.31
### 3.5 Corrélations les plus positives observées
- airports_per_million_people vs renewable_energy_pct (rho de Spearman = 0.47, n = 27)
- airports_per_million_people vs ecological_policy_index (rho de Spearman = 0.28, n = 27)
- airports_per_100k_km2 vs protected_areas_pct (rho de Spearman = 0.15, n = 27)
### 3.6 Corrélations les plus négatives observées
- local_density_mean vs ecological_policy_index (rho de Spearman = -0.51, n = 27)
- local_density_mean vs renewable_energy_pct (rho de Spearman = -0.50, n = 27)
- routes_per_airport vs renewable_energy_pct (rho de Spearman = -0.48, n = 27)
### 3.7 Lecture synthétique
Dans cet échantillon, il n'apparaît pas de relation unique entre orientation écologique et présence de grands aéroports. Les résultats suggèrent plutôt trois mécanismes:
1. **effet de géographie et d'insularité**: certains pays de petite taille ou insulaires peuvent cumuler forte orientation écologique et forte dépendance à quelques grands aéroports;
2. **effet de centralité économique**: des pays très intégrés au marché européen peuvent garder une activité aéroportuaire élevée tout en améliorant leurs indicateurs écologiques;
3. **effet de densité urbaine**: les grands aéroports des pays fortement urbanisés sont plus souvent entourés d'une densité locale élevée, ce qui concentre les arbitrages entre accessibilité et nuisances.
## 4. Typologie interprétative
### 4.1 Pays combinant orientation écologique forte et intensité aéroportuaire faible
- Bulgaria: 11.31
- Slovenia: 9.96
- Sweden: 15.74
- Poland: 14.80
- Slovakia: 8.81
### 4.2 Pays combinant orientation écologique forte et intensité aéroportuaire forte
- Luxembourg: 32.64
- Germany: 32.95
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
