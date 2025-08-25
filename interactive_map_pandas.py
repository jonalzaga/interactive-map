import folium
import pandas as pd

# Create the map centered on Ernio
m = folium.Map(location=[43.1733, -2.1369], zoom_start=10)

# Read mountain data from a CSV/TXT file
df = pd.read_csv("mountains_data.txt")

# Iterate over each row in the DataFrame
for _, row in df.iterrows():
    print(_)
    name = row["name"]           # Mountain name
    coords = [row["lat"], row["lon"]]  # Latitude and longitude
    climbed = bool(row["climbed"])     # Boolean (True if climbed, False otherwise)
    url = row["url"]             # URL with more info

    # Icon color depending on climbed status
    color = "green" if climbed else "red"  

    # --- Popup with clickable link ---
    popup_html = f"""
    <div style="text-align:center; font-size:14px; font-weight:bold;">
      <a href="{url}" target="_blank" rel="noopener noreferrer"
         style="color:black; text-decoration:none;"
         onmouseover="this.style.textDecoration='underline';"
         onmouseout="this.style.textDecoration='none';">
        {name}
      </a>
    </div>
    """

    folium.Marker(
        location=coords,
        icon=folium.Icon(color=color, icon="flag"),
        popup=folium.Popup(popup_html, max_width=250)
    ).add_to(m)

    # --- Visible label below the marker ---
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

# Save the map into an interactive HTML file
m.save("mountains_pandas.html")
