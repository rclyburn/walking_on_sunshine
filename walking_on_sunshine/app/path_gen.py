import openrouteservice


class PathGen:
    def __init__(self, key: str | None):
        self.client = openrouteservice.Client(key=key)

    def get_coords(self, location: str | list, distance: int) -> list:
        if isinstance(location, str):
            coordinates = self._addr_to_coords(location)
        else:
            coordinates = location

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

    def _addr_to_coords(self, addr: str):
        geocode = self.client.pelias_search(
            text=addr,
            validate=False,
        )

        coordinates = [
            list(geocode["features"][0]["geometry"]["coordinates"]),
        ]

        return coordinates

    def get_maps_url(self, downsampled_coords: list):
        pass

    def downsample_coords(self, route_coords):
        pass
