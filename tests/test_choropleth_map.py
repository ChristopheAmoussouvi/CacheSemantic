import json
from pathlib import Path

import pandas as pd

from src.components.choropleth_map import (
    build_agencies_choropleth,
    build_region_choropleth_with_points,
)


def make_dummy_df():
    return pd.DataFrame(
        [
            {"latitude": 48.8566, "longitude": 2.3522, "reclamation_rate": 0.15, "zone_code": "PAR", "name": "Agence Paris"},
            {"latitude": 45.7640, "longitude": 4.8357, "reclamation_rate": 0.25, "zone_code": "LYO", "name": "Agence Lyon"},
            {"latitude": 48.9, "longitude": 2.4, "reclamation_rate": 0.05, "zone_code": "PAR", "name": "Agence 2"},
        ]
    )


def load_sample_geojson():
    geo_path = Path(__file__).resolve().parents[1] / "choropleth" / "sample_polygons.geojson"
    with open(geo_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_build_agencies_choropleth_runs():
    df = make_dummy_df()
    m, count = build_agencies_choropleth(
        df,
        lat_col="latitude",
        lon_col="longitude",
        value_col="reclamation_rate",
        name_col="name",
        threshold=0.1,
    )
    assert m is not None
    assert isinstance(count, int)
    assert count >= 1  # at least those >= 0.1


def test_build_region_choropleth_with_points_runs():
    df = make_dummy_df()
    polygons = load_sample_geojson()
    m, count_points, count_polygons = build_region_choropleth_with_points(
        df,
        polygons_geojson=polygons,
        join_key_geo="code",
        join_key_df="zone_code",
        lat_col="latitude",
        lon_col="longitude",
        value_col="reclamation_rate",
        name_col="name",
        threshold=0.0,
    )
    assert m is not None
    assert isinstance(count_points, int) and count_points >= 1
    assert isinstance(count_polygons, int) and count_polygons >= 1
