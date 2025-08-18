import os
import subprocess
from random import randint

import openrouteservice

from walking_on_sunshine.common.logging.logger import get_logger

logger = get_logger(__name__)

import folium


class PathGen:
    def __init__(self, key: str | None):
        self.client = openrouteservice.Client(key=key)

    def _get_coords_from_addr(self, location: str, distance: float) -> list:
        coordinates = self._addr_to_coords(location)

        route = self.client.directions(
            coordinates=coordinates,
            profile="foot-walking",
            format="geojson",
            instructions=True,
            validate=False,
            options={
                "avoid_features": ["fords", "ferries"],
                "profile_params": {"weightings": {"green": 1, "quiet": 0}},
                "round_trip": {"length": distance, "points": 20},
            },
        )

        coord_list = list(route["features"][0]["geometry"]["coordinates"])
        return coord_list

    def _get_coords_from_list(self, location: list[float], distance: float) -> list:
        route = self.client.directions(
            coordinates=location,
            profile="foot-walking",
            format="geojson",
            instructions=True,
            validate=False,
            options={
                "avoid_features": ["fords", "ferries"],
                "profile_params": {"weightings": {"green": 0, "quiet": 0}},
                "round_trip": {"length": distance, "points": 100, "seed": 3},
            },
        )

        coord_list = list(route["features"][0]["geometry"]["coordinates"])

        folium.PolyLine(
            locations=[list(reversed(coord)) for coord in route["features"][0]["geometry"]["coordinates"]]
        ).add_to(m)

        m.save("index.html")

        wsl_path = os.path.abspath("index.html")
        windows_path = subprocess.check_output(["wslpath", "-w", wsl_path]).decode().strip()

        subprocess.run(["explorer.exe", windows_path])  # opens the map file in the users default browser
        return coord_list

    def _addr_to_coords(self, addr: str):
        geocode = self.client.pelias_search(
            text=addr,
            validate=False,
        )

        coordinates = [
            list(geocode["features"][0]["geometry"]["coordinates"]),
        ]

        return coordinates

    def _get_maps_url(self, route_coords: list):
        downsampled_coords = self._downsample_coords(route_coords)

        waypoints = []

        for coord in downsampled_coords[1:-1]:  # Exclude start/end
            waypoints.append(f"{coord[1]},{coord[0]}")

        start = f"{downsampled_coords[0][1]},{downsampled_coords[0][0]}"
        end = f"{downsampled_coords[-1][1]},{downsampled_coords[-1][0]}"

        base_url = "https://www.google.com/maps/dir/"
        waypoint_str = "/".join(waypoints)

        if waypoints:
            url = f"{base_url}{start}/{waypoint_str}/{end}/"
        else:
            url = f"{base_url}{start}/{end}/"

        return url

    def _downsample_coords(self, route_coords, max_waypoints=23):
        if len(route_coords) > max_waypoints + 1:
            step = len(route_coords) // (max_waypoints + 1)
            sampled_coords = route_coords[::step]
            if route_coords[-1] not in sampled_coords:
                sampled_coords.append(route_coords[-1])
            route_coords = sampled_coords

        return route_coords

    def generate_path(self, location: str, album_length: int):
        walking_speed_kmh = 2.5
        distance_km = (album_length / 3_600_000) * walking_speed_kmh
        distance_m = distance_km * 1000

        route_coords = self._get_coords_from_addr(location, distance_m)

        sampled_coords = self._downsample_coords(route_coords)

        return self._get_maps_url(sampled_coords)
