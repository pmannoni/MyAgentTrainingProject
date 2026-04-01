from pathlib import Path

EU_COUNTRIES = {
    "AT": "Austria",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "HR": "Croatia",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "DK": "Denmark",
    "EE": "Estonia",
    "FI": "Finland",
    "FR": "France",
    "DE": "Germany",
    "GR": "Greece",
    "HU": "Hungary",
    "IE": "Ireland",
    "IT": "Italy",
    "LV": "Latvia",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MT": "Malta",
    "NL": "Netherlands",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "ES": "Spain",
    "SE": "Sweden",
}

OURAIRPORTS_URL = "https://ourairports.com/data/airports.csv"
OPENFLIGHTS_ROUTES_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
GEONAMES_CITIES5000_URL = "https://download.geonames.org/export/dump/cities5000.zip"
WORLDBANK_API = "https://api.worldbank.org/v2/country/{iso2}/indicator/{indicator}?format=json&per_page=200"
RESTCOUNTRIES_URL = "https://restcountries.com/v3.1/region/europe?fields=cca2,name,population,area"

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = Path("outputs")
FIGURES_DIR = OUTPUT_DIR / "figures"
TABLES_DIR = OUTPUT_DIR / "tables"

POP_RADIUS_KM = 25.0
AIRPORT_TYPES_FILTER = ("large_airport",)
COUNTRY_MAP_METRICS = (
    "airports_per_100k_km2",
    "airports_per_million_people",
    "routes_per_airport",
    "local_density_mean",
    "population_density_country",
)
