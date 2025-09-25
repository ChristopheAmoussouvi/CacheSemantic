from __future__ import annotations

from typing import Optional, List

import folium
from folium.plugins import Search, MarkerCluster, Fullscreen, MiniMap
from branca.colormap import LinearColormap
import math



def _guess_center(latitudes: List[float], longitudes: List[float]) -> tuple[float, float]:
    if not latitudes or not longitudes:
        return 46.2276, 2.2137  # Center of France as default
    return float(sum(latitudes) / len(latitudes)), float(sum(longitudes) / len(longitudes))


def build_agencies_choropleth(
    df,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    value_col: str = "reclamation_rate",
    name_col: Optional[str] = None,
    threshold: Optional[float] = None,
    initial_zoom: int = 6,
) -> tuple[folium.Map, int]:
    """Build a folium choropleth-like map from agency coordinates and a value.

    - Colors circle markers by a continuous colormap based on value_col.
    - Integrates a search bar (by name_col if provided, else index).
    - Applies an optional threshold filter to only show points above threshold.

    Returns: (map, count_points_displayed)
    """
    if df is None or df.empty:
        m = folium.Map(location=(46.2276, 2.2137), zoom_start=5, tiles="cartodbpositron")
        return m, 0

    # Filter rows by numeric availability
    working = df.copy()
    # Keep only finite numeric rows for lat/lon/value
    working = working.dropna(subset=[lat_col, lon_col, value_col])
    try:
        working = working[(working[lat_col].astype(float).abs() <= 90) & (working[lon_col].astype(float).abs() <= 180)]
    except (KeyError, TypeError, ValueError):
        pass

    if threshold is not None:
        try:
            working = working[working[value_col].astype(float) >= float(threshold)]
        except (TypeError, ValueError):
            # If cannot cast, skip filtering
            pass

    if working.empty:
        m = folium.Map(location=(46.2276, 2.2137), zoom_start=5, tiles="cartodbpositron")
        return m, 0

    latitudes = working[lat_col].astype(float).tolist()
    longitudes = working[lon_col].astype(float).tolist()
    center = _guess_center(latitudes, longitudes)

    # Map
    m = folium.Map(location=center, zoom_start=initial_zoom, tiles="cartodbpositron", control_scale=True)
    Fullscreen().add_to(m)
    MiniMap(toggle_display=True).add_to(m)

    # Color scale
    try:
        vals = working[value_col].astype(float)
    except (KeyError, TypeError, ValueError):
        vals = working[value_col]
    vmin, vmax = float(vals.min()), float(vals.max())
    if vmin == vmax:
        vmax = vmin + 1e-9
    cmap = LinearColormap(["#1a9850", "#fee08b", "#d73027"], vmin=vmin, vmax=vmax)
    cmap.caption = f"{value_col}"
    cmap.add_to(m)

    # Marker cluster for performance
    cluster = MarkerCluster(name="Agences").add_to(m)

    # Build a GeoJson feature collection for Search
    features = []

    for _, row in working.iterrows():
        lat = float(row[lat_col])
        lon = float(row[lon_col])
        try:
            val = float(row[value_col])
        except (KeyError, TypeError, ValueError):
            continue
        name = str(row[name_col]) if name_col and name_col in working.columns else str(_)
        color = cmap(val)
        radius = 6 + 6 * ((val - vmin) / (vmax - vmin))
        popup_html = f"<b>{name}</b><br/>{value_col}: {val}"

        folium.CircleMarker(
            location=(lat, lon),
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=1,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(cluster)

        features.append({
            "type": "Feature",
            "properties": {"name": name, "value": val},
            "geometry": {"type": "Point", "coordinates": [lon, lat]}
        })

    # Add GeoJson layer for searching by name
    geojson = folium.GeoJson(
        data={"type": "FeatureCollection", "features": features},
        name="Index recherche",
        popup=None,
        show=False
    ).add_to(m)

    Search(
        layer=geojson,
        search_label="name",
        placeholder="Rechercher une agence…",
        collapsed=False,
        position="topleft"
    ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    return m, len(features)


def build_region_choropleth_with_points(
    df,
    polygons_geojson: dict,
    join_key_geo: str,
    join_key_df: str,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    value_col: str = "reclamation_rate",
    name_col: Optional[str] = None,
    threshold: Optional[float] = None,
    initial_zoom: int = 6,
    fill_palette: str = "YlOrRd",
) -> tuple[folium.Map, int, int]:
    """Build a polygon choropleth by communes/régions with agency points overlay.

    Requirements: df must contain a column (join_key_df) that matches a property in the GeoJSON (join_key_geo).
    """
    if df is None or df.empty or not polygons_geojson:
        m = folium.Map(location=(46.2276, 2.2137), zoom_start=5, tiles="cartodbpositron")
        return m, 0, 0

    working = df.copy()
    working = working.dropna(subset=[join_key_df, value_col, lat_col, lon_col])

    if threshold is not None:
        try:
            working = working[working[value_col].astype(float) >= float(threshold)]
        except Exception:
            pass

    if working.empty:
        m = folium.Map(location=(46.2276, 2.2137), zoom_start=5, tiles="cartodbpositron")
        return m, 0, 0

    # Aggregate by region key
    try:
        agg = working.groupby(join_key_df)[value_col].mean().reset_index()
    except Exception:
        agg = working[[join_key_df, value_col]].copy()

    # Compute map center from agency points
    try:
        latitudes = working[lat_col].astype(float).tolist()
        longitudes = working[lon_col].astype(float).tolist()
    except Exception:
        latitudes, longitudes = [], []
    center = _guess_center(latitudes, longitudes)

    m = folium.Map(location=center, zoom_start=initial_zoom, tiles="cartodbpositron", control_scale=True)
    Fullscreen().add_to(m)
    MiniMap(toggle_display=True).add_to(m)

    # Determine value range for colormap
    try:
        vmin, vmax = float(agg[value_col].min()), float(agg[value_col].max())
    except Exception:
        vmin, vmax = 0.0, 1.0
    if math.isfinite(vmin) and math.isfinite(vmax) and vmin == vmax:
        vmax = vmin + 1e-9

    # Choropleth layer
    ch = folium.Choropleth(
        geo_data=polygons_geojson,
        name="Choropleth",
        data=agg,
        columns=[join_key_df, value_col],
        key_on=f"feature.properties.{join_key_geo}",
        fill_color=fill_palette,
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color="lightgray",
        legend_name=f"{value_col} (moyenne par zone)",
    ).add_to(m)

    # Tooltip on polygons
    try:
        folium.GeoJsonTooltip(fields=[join_key_geo], aliases=["Zone:"]).add_to(ch.geojson)
    except AttributeError:
        pass

    # Add agency markers colored by value
    try:
        vals = working[value_col].astype(float)
        vmin_pts, vmax_pts = float(vals.min()), float(vals.max())
        if vmin_pts == vmax_pts:
            vmax_pts = vmin_pts + 1e-9
    except (KeyError, TypeError, ValueError):
        vmin_pts, vmax_pts = vmin, vmax

    cmap = LinearColormap(["#1a9850", "#fee08b", "#d73027"], vmin=vmin_pts, vmax=vmax_pts)
    cmap.caption = f"{value_col} (agences)"
    cmap.add_to(m)

    cluster = MarkerCluster(name="Agences").add_to(m)

    features = []
    for idx, row in working.iterrows():
        try:
            lat = float(row[lat_col]); lon = float(row[lon_col])
            val = float(row[value_col])
        except (KeyError, TypeError, ValueError):
            continue
        name = str(row[name_col]) if name_col and name_col in working.columns else str(idx)
        color = cmap(val)
        radius = 6 + 6 * ((val - vmin_pts) / (vmax_pts - vmin_pts)) if (vmax_pts - vmin_pts) else 6
        popup_html = f"<b>{name}</b><br/>{value_col}: {val}"
        folium.CircleMarker(
            location=(lat, lon),
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=1,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(cluster)

        features.append({
            "type": "Feature",
            "properties": {"name": name, "value": val},
            "geometry": {"type": "Point", "coordinates": [lon, lat]}
        })

    geojson = folium.GeoJson(
        data={"type": "FeatureCollection", "features": features},
        name="Index recherche",
        popup=None,
        show=False
    ).add_to(m)
    Search(layer=geojson, search_label="name", placeholder="Rechercher une agence…", collapsed=False, position="topleft").add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    # Return map, agencies count, polygons count
    poly_count = len(polygons_geojson.get("features", [])) if isinstance(polygons_geojson, dict) else 0
    return m, len(features), poly_count


def export_map_html_bytes(m: folium.Map) -> bytes:
    """Return a standalone HTML for download as bytes."""
    html = m.get_root().render()
    return html.encode("utf-8")

