#!/usr/bin/env python3
"""
Interactive map of mountains in Gipuzkoa and Navarra.

- Province polygons from 'data/georef-spain-provincia.json'
- Dataset from 'data/montes_gipuzkoa_coords.txt' with columns:
  name, lat, lon, climbed, url, province, challenge

Markers:
- Green if climbed, red otherwise
- Popup with clickable link
- Label under the marker

Layers:
- Gipuzkoa (all its mountains + polygon)
- Navarra  (all its mountains + polygon)
- Challenge (35) (only challenge peaks + Gipuzkoa polygon in a different color)

Output:
- docs/index.html (for GitHub Pages)

Notes
-----
This module is intentionally small and self-contained. Functions are written to be
side-effect free except where they explicitly mutate a Folium map/layer. Data
loading is separated from rendering to keep responsibilities clear.
"""
from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Any, Dict, Tuple

import folium
import pandas as pd

# --- Paths ---
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT_HTML = ROOT / "docs" / "index.html"

PROVINCES_FILE = DATA / "georef-spain-provincia.json"
MOUNTAINS_FILE = DATA / "mountains_data.txt"
JAPAN_FILE = DATA / "world.json"

# --- Map config ---
MAP_CENTER: Tuple[float, float] = (43.1733, -2.1369)
MAP_ZOOM = 10
COLOR_GIPUZKOA = "blue"
COLOR_NAVARRA = "red"
COLOR_JAPAN = "red"
COLOR_CHALLENGE = "purple"
ICON_CLIMBED: Dict[bool, str] = {True: "green", False: "red"}


def add_poly(
    group: folium.FeatureGroup,
    data: Dict[str, Any],
    fill_color: str,
    border_color: str,
) -> None:
    """Add a filled polygon (GeoJSON) to a Folium layer.

    This is a thin wrapper over :class:`folium.GeoJson` that applies a consistent
    style (fill, opacity, stroke) so province polygons look uniform across the map.

    Args:
        group: Target layer to which the polygon will be added.
        data: A GeoJSON-like mapping (already extracted from the provinces file).
        fill_color: Fill color for the polygon body.
        border_color: Stroke color for the polygon outline.

    Side Effects:
        Mutates ``group`` by attaching a new GeoJSON object.
    """
    folium.GeoJson(
        data=data,
        style_function=lambda _: {
            "fillColor": fill_color,
            "fillOpacity": 0.3,
            "color": border_color,
            "weight": 3,
            "opacity": 0.8,
        },
    ).add_to(group)


def add_marker_and_label(
    lat: float,
    lon: float,
    name: str | None,
    url: str | None,
    color: str,
    group: folium.FeatureGroup,
) -> None:
    """Add a mountain marker plus a static text label at the same coordinates.

    Two markers are added:
      1) A standard pin with a colored icon and a clickable popup linking to ``url``.
      2) A label rendered via :class:`folium.DivIcon` placed slightly below the pin.

    The duplication is deliberate: Folium does not provide an out-of-the-box
    "marker with subtitle" primitive. This pattern keeps label styling simple while
    preserving interactive popups on click.

    Args:
        lat: Latitude of the mountain.
        lon: Longitude of the mountain.
        name: Display name; will be HTML-escaped.
        url: Optional external link; will be HTML-escaped. ``#`` if absent.
        color: Icon color (e.g., "green" for climbed, "red" otherwise).
        group: Layer to attach both the pin and its label to.

    Side Effects:
        Mutates ``group`` by attaching two markers.
    """
    safe_name = html.escape(str(name or ""))
    safe_url = html.escape(str(url or "#"))

    popup_html = f"""
    <div style="text-align:center; font-weight:bold">
        <a href="{safe_url}" target="_blank" rel="noopener noreferrer" style="color:black">
            {safe_name}
        </a>
    </div>
    """

    # Interactive pin
    folium.Marker(
        [lat, lon],
        icon=folium.Icon(color=color, icon="flag"),
        popup=folium.Popup(popup_html, max_width=250),
    ).add_to(group)

    # Readable label under the pin (non-interactive)
    folium.Marker(
        [lat, lon],
        icon=folium.DivIcon(
            html=f"""
            <div style="pointer-events:none; text-align:center;
                        transform: translate(-50%, 25px);
                        font-size:12px; font-weight:bold; color:black;">
                {safe_name}
            </div>
            """
        ),
    ).add_to(group)


def load_provinces(name: str, path: Path) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Load province polygons and return the GeoJSON shapes for Gipuzkoa and Navarra.

    The provinces file contains a list of province records where each record has
    a ``prov_name`` and a nested ``geo_shape``. We extract the shapes by name.

    Args:
        path: Filesystem path to the provinces GeoJSON file.

    Returns:
        A pair ``(gipuzkoa_shape, navarra_shape)`` suitable to feed into Folium.

    Raises:
        ``StopIteration`` if either province cannot be found (input is malformed).
    """
    with path.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    if name == "Japan":
        return next(x["geometry"] for x in data["features"] if x["properties"]["NAME"] == name)
    else:
        return next(x["geo_shape"] for x in data if x["prov_name"] == name)

    


def load_mountains(path: Path) -> pd.DataFrame:
    """Load the mountains dataset and validate the required schema.

    The input is expected to be a CSV (``.txt`` is fine as long as it is CSV-formatted)
    with at least these columns: ``name, lat, lon, climbed, url, province, challenge``.

    Args:
        path: Filesystem path to the mountains CSV/TXT file.

    Returns:
        A :class:`pandas.DataFrame` ready for iteration and filtering.

    Raises:
        ValueError: If required columns are missing.
    """
    df = pd.read_csv(path)
    required = ["name", "lat", "lon", "climbed", "url", "province", "challenge"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    return df


def build_map() -> folium.Map:
    """Construct the interactive Folium map with layers and markers.

    Pipeline:
        1) Create the base map and add the base tile layer.
        2) Load province GeoJSON and create three feature groups: Gipuzkoa, Navarra,
           and Challenge (35).
        3) Render province polygons into their groups using consistent styles.
        4) Load mountain rows, skip any without valid coordinates, and add markers to
           their respective province group. Challenge mountains are also mirrored into
           the Challenge group.
        5) Attach a non-collapsed layer control for easy toggling.

    Returns:
        A fully populated :class:`folium.Map` instance ready to be saved.
    """
    m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles=None)
    folium.TileLayer("OpenStreetMap", name="Base map").add_to(m)

    gip_geo = load_provinces("Gipuzkoa",PROVINCES_FILE)
    nav_geo = load_provinces("Navarra", PROVINCES_FILE)
    japan_geo = load_provinces("Japan", JAPAN_FILE)

    fg_gip = folium.FeatureGroup(name="Gipuzkoa", show=True).add_to(m)
    fg_nav = folium.FeatureGroup(name="Navarra", show=True).add_to(m)
    fg_chal = folium.FeatureGroup(name="Challenge (35)").add_to(m)
    fg_japan = folium.FeatureGroup(name="Japan", show=True).add_to(m)

    add_poly(fg_gip, gip_geo, fill_color=COLOR_GIPUZKOA, border_color=COLOR_GIPUZKOA)
    add_poly(fg_nav, nav_geo, fill_color=COLOR_NAVARRA, border_color=COLOR_NAVARRA)
    add_poly(fg_chal, gip_geo, fill_color=COLOR_CHALLENGE, border_color=COLOR_CHALLENGE)
    add_poly(fg_japan, japan_geo, fill_color=COLOR_JAPAN, border_color=COLOR_JAPAN)

    df = load_mountains(MOUNTAINS_FILE)

    for _, r in df.iterrows():
        lat, lon = r.get("lat"), r.get("lon")

        # Skip rows without valid coordinates
        if (
            lat is None
            or lon is None
            or (isinstance(lat, float) and math.isnan(lat))
            or (isinstance(lon, float) and math.isnan(lon))
        ):
            continue

        prov = (r.get("province") or "").strip()
        color = ICON_CLIMBED[bool(r.get("climbed", False))]
        is_chal = bool(r.get("challenge", False))

        if prov == "Gipuzkoa":
            add_marker_and_label(lat, lon, r.get("name"), r.get("url"), color, fg_gip)
            if is_chal:
                add_marker_and_label(lat, lon, r.get("name"), r.get("url"), color, fg_chal)
        elif prov == "Navarra":
            add_marker_and_label(lat, lon, r.get("name"), r.get("url"), color, fg_nav)
        elif prov == "Japan":
            add_marker_and_label(lat, lon, r.get("name"), r.get("url"), color, fg_japan)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def main() -> None:
    """Entrypoint: build the map and persist it to ``OUT_HTML``.

    Ensures the output directory exists (``parents=True`` to create missing
    directories; ``exist_ok=True`` to avoid errors if already present), then builds
    and saves the map. Prints the absolute path of the generated file for quick
    inspection when run from the CLI.
    """
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    m = build_map()
    m.save(str(OUT_HTML))
    print(f"Map saved → {OUT_HTML.resolve()}")


if __name__ == "__main__":
    main()
