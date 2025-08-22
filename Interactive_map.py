import folium

# Center map on Ernio
m = folium.Map(location=[43.1733, -2.1369], zoom_start=10)

mountains = {
    "Txindoki": [43.02290543492231, -2.0887569426439403],
    "Aizkorri": [43.0358, -2.3581],
    "Ernio": [43.1844, -2.1069],
    "Adarra": [43.2506, -2.0439],
    "Jaizkibel": [43.3586, -1.8614],
    "Peñas de Aia": [43.3072, -1.8175],
}

# Add markers with bold labels
for name, coords in mountains.items():
    # Default marker
    folium.Marker(
        location=coords,
        icon=folium.Icon(color="green", icon="info-sign"),
    ).add_to(m)

    # Fixed bold label under the marker
    folium.map.Marker(
        location=coords,
        icon=folium.DivIcon(
            html=f"""
                <div style="text-align:center;
                            transform: translate(-50%, 25px);
                            font-size: 12px;
                            font-weight: bold;
                            color: black;">
                    {name}
                </div>
            """
        )
    ).add_to(m)

m.save("mountains.html")
