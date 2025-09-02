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
"""
from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Any, Dict

import folium
import pandas as pd

# --- Paths ---
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT_HTML = ROOT / "docs" / "index.html"

PROVINCES_FILE = DATA / "georef-spain-provincia.json"
MOUNTAINS_FILE = DATA / "mountains_data.txt"

# --- Map config ---
MAP_CENTER = (43.1733, -2.1369)
MAP_ZOOM = 10
COLOR_CHALLENGE_POLY = "purple"
ICON_CLIMBED = {True: "green", False: "red"}


def add_poly(group: folium.FeatureGroup, data: Dict[str, Any], fill: str, stroke: str) -> None:
    folium.GeoJson(
        data=data,
        style_function=lambda _: {
            "fillColor": fill,
            "fillOpacity": 0.3,
            "color": stroke,
            "weight": 3,
            "opacity": 0.8,
        },
    ).add_to(group)


def add_marker_and_label(lat, lon, name, url, color, group) -> None:
    safe_name = html.escape(str(name or ""))
    safe_url = html.escape(str(url or "#"))

    popup_html = f"""
    <div style="text-align:center; font-weight:bold">
        <a href="{safe_url}" target="_blank" rel="noopener noreferrer" style="color:black">
            {safe_name}
        </a>
    </div>
    """

    folium.Marker(
        [lat, lon],
        icon=folium.Icon(color=color, icon="flag"),
        popup=folium.Popup(popup_html, max_width=250),
    ).add_to(group)

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


def load_provinces(path: Path) -> tuple[Dict[str, Any], Dict[str, Any]]:
    with path.open(encoding="utf-8-sig") as f:
        data = json.load(f)
    gip = next(x["geo_shape"] for x in data if x["prov_name"] == "Gipuzkoa")
    nav = next(x["geo_shape"] for x in data if x["prov_name"] == "Navarra")
    return gip, nav


def load_mountains(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = ["name", "lat", "lon", "climbed", "url", "province", "challenge"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    return df


def build_map() -> folium.Map:
    m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles=None)
    folium.TileLayer("OpenStreetMap", name="Base map").add_to(m)

    gip_geo, nav_geo = load_provinces(PROVINCES_FILE)

    fg_gip = folium.FeatureGroup(name="Gipuzkoa", show=True).add_to(m)
    fg_nav = folium.FeatureGroup(name="Navarra", show=True).add_to(m)
    fg_chal = folium.FeatureGroup(name="Challenge (35)").add_to(m)

    add_poly(fg_gip, gip_geo, "blue", "blue")
    add_poly(fg_nav, nav_geo, "red", "red")
    add_poly(fg_chal, gip_geo, COLOR_CHALLENGE_POLY, COLOR_CHALLENGE_POLY)

    df = load_mountains(MOUNTAINS_FILE)

    for _, r in df.iterrows():
        lat, lon = r.get("lat"), r.get("lon")
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

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def main() -> None:
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    m = build_map()
    m.save(str(OUT_HTML))
    print(f"Map saved → {OUT_HTML.resolve()}")


if __name__ == "__main__":
    main()
