import folium
import pandas as pd

# Create a map centered on Ernio with an initial zoom level of 10
m = folium.Map(location=[43.1733, -2.1369], zoom_start=10)

# Read mountain data from a CSV (or .txt) file into a pandas DataFrame
df = pd.read_csv("mountains_data.txt")
print(df)  # Print DataFrame to verify contents (optional)

# Iterate over the DataFrame rows one by one
for _, row in df.iterrows():
    name = row["name"]          # Mountain name
    coords = [row["lat"], row["lon"]]  # Latitude and longitude as a list
    climbed = row["climbed"]        # Boolean flag (True if climbed, False otherwise)

    # Conditional expression: choose color depending on climb status
    color = "green" if climbed else "red"  

    # Add a marker with a flag icon at the mountain's location
    # Color is green if climbed, red if not
    folium.Marker(
        location=coords,
        icon=folium.Icon(color=color, icon="flag"),
    ).add_to(m)

    # Add a bold text label below the marker showing the mountain's name
    # This uses a DivIcon with HTML/CSS to position and style the label
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

# Save the generated map into an interactive HTML file
m.save("mountains_pandas.html")
