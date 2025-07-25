import os
import pprint
import subprocess

import folium
import openrouteservice

key = os.getenv("OPENROUTE_API_KEY")
key = str(key)[1:]  # for some reason the key string was returning with an extra ' at the front


client = openrouteservice.Client(key=key)  # Specify your personal API key

address = "4050 17th St, San Francisco"

m = folium.Map(location=[37.76256, -122.436414], tiles="cartodbpositron", zoom_start=13)

geocode1 = client.pelias_search(
    text=address,
    focus_point=list(reversed(m.location)),
    validate=False,
)

geocode2 = client.pelias_search(
    text="3600 16th St, San Francisco, CA 94114",
    focus_point=list(reversed(m.location)),
    validate=False,
)

# pprint.pprint(geocode)

for result in geocode1["features"]:
    folium.Marker(
        location=list(reversed(result["geometry"]["coordinates"])),
        icon=folium.Icon(icon="compass", color="green", prefix="fa"),
        popup=folium.Popup(result["properties"]["name"]),
    ).add_to(m)


coordinates = [
    list(geocode1["features"][0]["geometry"]["coordinates"]),
<<<<<<< HEAD
=======
    # list(geocode1["features"][0]["geometry"]["coordinates"]),
>>>>>>> f05fd63 (working round trip)
]


route = client.directions(
    coordinates=coordinates,
    profile="foot-walking",
    format="geojson",
    instructions=False,
    validate=False,
    options={
        "avoid_features": ["fords", "ferries"],
        "profile_params": {"weightings": {"green": 1, "quiet": 0}},
        "round_trip": {
            "length": 2100,
            "points": 5,
        },
    },
)

folium.PolyLine(locations=[list(reversed(coord)) for coord in route["features"][0]["geometry"]["coordinates"]]).add_to(
    m
)


m.save("index.html")

wsl_path = os.path.abspath("index.html")
windows_path = subprocess.check_output(["wslpath", "-w", wsl_path]).decode().strip()

subprocess.run(["explorer.exe", windows_path])  # opens the map file in the users default browser
