import unittest

import pandas as pd

from eu_airports_analysis.policy_analysis import (
    build_policy_profiles,
    compute_spearman_correlations,
    merge_airport_and_policy,
)


class PolicyAnalysisTests(unittest.TestCase):
    def test_merge_airport_and_policy_adds_intensity_index(self):
        country_metrics = pd.DataFrame(
            [
                {
                    "country_iso2": "AA",
                    "country_name": "Aland",
                    "airports_total": 1,
                    "airports_per_100k_km2": 1.0,
                    "airports_per_million_people": 1.0,
                    "routes_per_airport": 10.0,
                    "local_density_mean": 50.0,
                },
                {
                    "country_iso2": "BB",
                    "country_name": "Borland",
                    "airports_total": 2,
                    "airports_per_100k_km2": 2.0,
                    "airports_per_million_people": 2.0,
                    "routes_per_airport": 20.0,
                    "local_density_mean": 100.0,
                },
            ]
        )
        policy_metrics = pd.DataFrame(
            [
                {"country_iso2": "AA", "country_name": "Aland", "ecological_policy_index": 40.0},
                {"country_iso2": "BB", "country_name": "Borland", "ecological_policy_index": 60.0},
            ]
        )
        merged = merge_airport_and_policy(country_metrics, policy_metrics)
        self.assertIn("airport_intensity_index", merged.columns)
        self.assertLess(merged.loc[0, "airport_intensity_index"], merged.loc[1, "airport_intensity_index"])

    def test_compute_spearman_correlations(self):
        df = pd.DataFrame(
            [
                {
                    "airports_total": 1,
                    "airports_per_100k_km2": 1,
                    "airports_per_million_people": 1,
                    "routes_per_airport": 1,
                    "local_density_mean": 1,
                    "renewable_energy_pct": 10,
                    "protected_areas_pct": 20,
                    "co2_per_capita": 3,
                    "ecological_policy_index": 30,
                },
                {
                    "airports_total": 2,
                    "airports_per_100k_km2": 2,
                    "airports_per_million_people": 2,
                    "routes_per_airport": 2,
                    "local_density_mean": 2,
                    "renewable_energy_pct": 20,
                    "protected_areas_pct": 30,
                    "co2_per_capita": 2,
                    "ecological_policy_index": 40,
                },
                {
                    "airports_total": 3,
                    "airports_per_100k_km2": 3,
                    "airports_per_million_people": 3,
                    "routes_per_airport": 3,
                    "local_density_mean": 3,
                    "renewable_energy_pct": 30,
                    "protected_areas_pct": 40,
                    "co2_per_capita": 1,
                    "ecological_policy_index": 50,
                },
            ]
        )
        corr = compute_spearman_correlations(df)
        row = corr[(corr["airport_metric"] == "airports_total") & (corr["policy_metric"] == "ecological_policy_index")].iloc[0]
        self.assertAlmostEqual(float(row["spearman_rho"]), 1.0, places=6)

    def test_build_policy_profiles(self):
        df = pd.DataFrame(
            [
                {"country_name": "A", "country_iso2": "A", "ecological_policy_index": 10, "airport_intensity_index": 10},
                {"country_name": "B", "country_iso2": "B", "ecological_policy_index": 20, "airport_intensity_index": 20},
                {"country_name": "C", "country_iso2": "C", "ecological_policy_index": 30, "airport_intensity_index": 30},
                {"country_name": "D", "country_iso2": "D", "ecological_policy_index": 40, "airport_intensity_index": 40},
                {"country_name": "E", "country_iso2": "E", "ecological_policy_index": 50, "airport_intensity_index": 50},
                {"country_name": "F", "country_iso2": "F", "ecological_policy_index": 60, "airport_intensity_index": 60},
            ]
        )
        profiles = build_policy_profiles(df)
        self.assertIn("profile_label", profiles.columns)
        self.assertEqual(profiles["policy_group"].nunique(), 3)


if __name__ == "__main__":
    unittest.main()

