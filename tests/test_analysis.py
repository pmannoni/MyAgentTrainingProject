import unittest

import numpy as np
import pandas as pd

from eu_airports_analysis.analysis import (
    build_country_metrics,
    compute_local_population_density_proxy,
    haversine_km,
)


class AnalysisTests(unittest.TestCase):
    def test_haversine_zero(self):
        dist = haversine_km(np.array([0.0]), np.array([0.0]), np.array([0.0]), np.array([0.0]))
        self.assertAlmostEqual(float(dist[0]), 0.0, places=8)

    def test_local_density_proxy_positive(self):
        airports = pd.DataFrame(
            [
                {
                    "icao": "TEST",
                    "name": "Test Airport",
                    "type": "medium_airport",
                    "country_iso2": "FR",
                    "country_name": "France",
                    "iata_code": "TST",
                    "lat": 48.8566,
                    "lon": 2.3522,
                    "route_connections": 10,
                }
            ]
        )
        cities = pd.DataFrame(
            [
                {"name": "Paris", "country_iso2": "FR", "lat": 48.8566, "lon": 2.3522, "population": 2_100_000},
                {"name": "FarCity", "country_iso2": "FR", "lat": 40.0, "lon": 2.0, "population": 500_000},
            ]
        )
        out = compute_local_population_density_proxy(airports, cities, radius_km=25)
        self.assertGreater(out.loc[0, "nearby_population_25km"], 2_000_000)

    def test_country_metrics(self):
        airports_enriched = pd.DataFrame(
            [
                {
                    "icao": "AAA",
                    "country_iso2": "FR",
                    "country_name": "France",
                    "type": "large_airport",
                    "route_connections": 100,
                    "local_density_proxy_pop_per_km2": 200,
                },
                {
                    "icao": "BBB",
                    "country_iso2": "FR",
                    "country_name": "France",
                    "type": "medium_airport",
                    "route_connections": 50,
                    "local_density_proxy_pop_per_km2": 100,
                },
            ]
        )
        stats = pd.DataFrame(
            [{"country_iso2": "FR", "country_name": "France", "population": 68_000_000, "surface_km2": 549_087}]
        )
        out = build_country_metrics(airports_enriched, stats)
        self.assertEqual(int(out.loc[0, "airports_total"]), 2)
        self.assertAlmostEqual(float(out.loc[0, "routes_per_airport"]), 75.0, places=6)


if __name__ == "__main__":
    unittest.main()

