import base64
from random import randint

import folium
import openrouteservice


class PathGen:
    def __init__(self, key: str | None):
        self.client = openrouteservice.Client(key=key)

    def _parse_coordinate_string(self, location: str) -> tuple[float, float] | None:
        if not location:
            return None
        parts = [part.strip() for part in location.split(",")]
        if len(parts) != 2:
            return None
        try:
            lat = float(parts[0])
            lon = float(parts[1])
        except ValueError:
            return None
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        return lat, lon

    def _get_coords_from_addr(self, location: str, distance: float) -> list:
        coordinates = self._addr_to_coords(location)[0]  # Get the first coordinate pair

        route = self.client.directions(
            coordinates=[coordinates],  # Use as starting point for round trip
            profile="foot-walking",
            format="geojson",
            instructions=True,
            validate=False,
            options={
                "avoid_features": ["fords", "ferries"],
                "profile_params": {"weightings": {"green": 1, "quiet": 0}},
                "round_trip": {"length": distance, "points": 20, "seed": randint(1, 10000)},
            },
        )

        coord_list = list(route["features"][0]["geometry"]["coordinates"])
        return coord_list

    def _get_coords_from_list(self, location: list[list[float]], distance: float) -> list:
        route = self.client.directions(
            coordinates=location,
            profile="foot-walking",
            format="geojson",
            instructions=True,
            validate=False,
            options={
                "avoid_features": ["fords", "ferries"],
                "profile_params": {"weightings": {"green": 1, "quiet": 0}},
                "round_trip": {"length": distance, "points": 100, "seed": randint(1, 10000)},
            },
        )

        coord_list = list(route["features"][0]["geometry"]["coordinates"])
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

    def _coords_to_addr(self, lat: float, lon: float) -> str | None:
        reverse = getattr(self.client, "pelias_reverse", None)
        if reverse is None:
            return None
        try:
            result = reverse(point=[lon, lat], size=1, validate=False)
        except Exception:
            return None

        features = result.get("features") if isinstance(result, dict) else None
        if not features:
            return None

        props = features[0].get("properties", {})
        return props.get("label") or props.get("name")

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
        if len(route_coords) > max_waypoints + 2:
            step = len(route_coords) // (max_waypoints + 1)
            sampled_coords = route_coords[::step]
            if route_coords[-1] not in sampled_coords:
                sampled_coords[-1] = route_coords[-1]
            route_coords = sampled_coords

        return route_coords

    def _build_folium_map(self, coords: list[list[float]]) -> str | None:
        try:
            latlngs = [
                (lat, lon) for lon, lat in coords if isinstance(lat, (float, int)) and isinstance(lon, (float, int))
            ]
            if len(latlngs) < 2:
                return None

            mid_index = len(latlngs) // 2
            midpoint = latlngs[mid_index]

            fmap = folium.Map(location=midpoint, zoom_start=13, control_scale=True, tiles="cartodbpositron")
            folium.PolyLine(latlngs, weight=6, opacity=0.85, color="#4f46e5").add_to(fmap)
            folium.CircleMarker(latlngs[0], radius=6, color="#fff", weight=2, fill=True, fill_color="#4f46e5").add_to(
                fmap
            )
            folium.CircleMarker(latlngs[-1], radius=6, color="#fff", weight=2, fill=True, fill_color="#4338ca").add_to(
                fmap
            )

            fmap.fit_bounds(latlngs, padding=(30, 30))

            html = fmap.get_root().render()
            return "data:text/html;base64," + base64.b64encode(html.encode("utf-8")).decode("ascii")
        except Exception:
            return None

    def generate_path(self, location: str, album_length: int) -> tuple[str, str, list[dict[str, float]], str | None]:
        walking_speed_kmh = 2.5
        distance_km = (album_length / 3_600_000) * walking_speed_kmh
        distance_m = distance_km * 1000

        resolved_location = location
        coord_pair = self._parse_coordinate_string(location)
        if coord_pair:
            lat, lon = coord_pair
            addr = self._coords_to_addr(lat, lon)
            if addr:
                resolved_location = addr
                route_coords = self._get_coords_from_addr(resolved_location, distance_m)
            else:
                route_coords = self._get_coords_from_list([[lon, lat]], distance_m)
        else:
            route_coords = self._get_coords_from_addr(resolved_location, distance_m)

        sampled_coords = self._downsample_coords(route_coords)

        preview_coords = [{"lat": coord[1], "lon": coord[0]} for coord in sampled_coords]
        map_embed = self._build_folium_map(route_coords)

        return self._get_maps_url(sampled_coords), resolved_location, preview_coords, map_embed
