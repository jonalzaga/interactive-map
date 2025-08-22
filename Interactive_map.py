import folium

# Create a map centered on Ernio with an initial zoom level of 10
m = folium.Map(location=[43.1733, -2.1369], zoom_start=10)

# Dictionary of mountains:
# Each key is the mountain name, and each value contains:
#   - "coords": a list with latitude and longitude
#   - "climbed": a boolean flag indicating if the mountain has been climbed (True = green, False = red)
mountains = {
    "Txindoki": {"coords": [43.0229, -2.0887], "climbed": True},
    "Aizkorri": {"coords": [43.0358, -2.3581], "climbed": True},
    "Ernio": {"coords": [43.1844, -2.1069], "climbed": True},
    "Adarra": {"coords": [43.2506, -2.0439], "climbed": True},
    "Jaizkibel": {"coords": [43.3586, -1.8614], "climbed": True},
    "Peñas de Aia": {"coords": [43.3072, -1.8175], "climbed": True},
    "Izarraitz (Erlo)": {"coords": [43.2683, -2.2914], "climbed": True},
    "Uzturre": {"coords": [43.1347, -2.0481], "climbed": False},
    "Igeldo": {"coords": [43.3078, -2.0272], "climbed": True},
    "Irimo": {"coords": [43.1522, -2.2742], "climbed": True},
    "Andutz": {"coords": [43.2850, -2.3539], "climbed": True},
    "Kukuarri": {"coords": [43.2947, -2.0503], "climbed": True}
}

# Iterate through the mountains dictionary
for name, data in mountains.items():
    coords = data["coords"]               # Geographic coordinates (lat, lon)
    color = "green" if data["climbed"] else "red"  # Green if climbed, red if not, conditional expression

    # Add a marker with a flag icon, colored according to climb status
    folium.Marker(
        location=coords,
        icon=folium.Icon(color=color, icon="flag"),
    ).add_to(m)

    # Add a text label below the marker with the mountain name
    # This uses a DivIcon to render custom HTML with CSS positioning
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

# Save the generated interactive map as an HTML file
m.save("mountains.html")
