import json
import unittest
from pathlib import Path

import pandas as pd

from src.components.choropleth_map import (
    build_agencies_choropleth,
    build_region_choropleth_with_points,
)


class TestChoroplethMap(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            [
                {"latitude": 48.8566, "longitude": 2.3522, "reclamation_rate": 0.15, "zone_code": "PAR", "name": "Agence Paris"},
                {"latitude": 45.7640, "longitude": 4.8357, "reclamation_rate": 0.25, "zone_code": "LYO", "name": "Agence Lyon"},
                {"latitude": 48.9, "longitude": 2.4, "reclamation_rate": 0.05, "zone_code": "PAR", "name": "Agence 2"},
            ]
        )
        geo_path = Path(__file__).resolve().parents[1] / "choropleth" / "sample_polygons.geojson"
        with open(geo_path, "r", encoding="utf-8") as f:
            self.polygons = json.load(f)

    def test_agencies_points_map(self):
        m, count = build_agencies_choropleth(
            self.df,
            lat_col="latitude",
            lon_col="longitude",
            value_col="reclamation_rate",
            name_col="name",
            threshold=0.1,
        )
        self.assertIsNotNone(m)
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 1)

    def test_polygon_plus_points_map(self):
        m, count_points, count_polygons = build_region_choropleth_with_points(
            self.df,
            polygons_geojson=self.polygons,
            join_key_geo="code",
            join_key_df="zone_code",
            lat_col="latitude",
            lon_col="longitude",
            value_col="reclamation_rate",
            name_col="name",
            threshold=0.0,
        )
        self.assertIsNotNone(m)
        self.assertIsInstance(count_points, int)
        self.assertGreaterEqual(count_points, 1)
        self.assertIsInstance(count_polygons, int)
        self.assertGreaterEqual(count_polygons, 1)


if __name__ == "__main__":
    unittest.main()
