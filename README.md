# EU Airports Analysis

This project builds an EU-focused airport analysis for large airports only and compares countries on:

- Number of large airports
- Large airports vs. country surface area
- Large airports vs. population
- Airport activity (proxy based on published route connectivity)
- Nearby population density around each airport (proxy from nearby city populations)
- Country population density and country-level airport indicators on maps

## Data sources

- OurAirports: airport metadata and locations
- OpenFlights routes: route connections proxy for airport activity
- World Bank API / RestCountries: country population and surface area
- GeoNames cities5000: nearby population proxy around airport coordinates

## Outputs

After running, files are generated in:

- `data/processed/airports_enriched.csv`
- `outputs/tables/country_metrics.csv`
- `outputs/tables/extreme_countries_summary.csv`
- `outputs/figures/eu_airports_map.html`
- `outputs/figures/airports_vs_surface.png`
- `outputs/figures/airports_vs_population.png`
- `outputs/figures/activity_proxy_by_country.png`
- `outputs/figures/nearby_density_proxy_by_country.png`
- `outputs/figures/airports_per_million_people.png`
- `outputs/figures/route_connections_distribution_top10.png`
- `outputs/figures/country_map_airports_per_100k_km2.html`
- `outputs/figures/country_map_airports_per_million_people.html`
- `outputs/figures/country_map_routes_per_airport.html`
- `outputs/figures/country_map_local_density_mean.html`
- `outputs/figures/country_map_population_density_country.html`
- `outputs/figures/population_density_cities_map.html`
- `outputs/figures/airport_local_density_map.html`
- `outputs/figures/country_population_density_map.html`

## Quick start

```powershell
python -m pip install -r requirements.txt
python main.py --refresh
```

## Run tests

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## Notes

- "Airport activity" here uses route connectivity as a proxy (number of published route links), not direct passenger counts.
- "Nearby population density" is a proxy based on GeoNames city populations within a 25 km radius around airports.
