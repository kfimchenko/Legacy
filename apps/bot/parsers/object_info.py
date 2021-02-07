from dataclasses import dataclass


@dataclass
class Location:
    latitude: float
    longitude: float


@dataclass
class ObjectInfo:
    name: str
    date: str
    address: str
    photo_url: str
    location: Location
    distance: float


def parse_object_info(data) -> ObjectInfo:
    def parse(response):
        coordinates = response.get('Coordinate', {})

        return ObjectInfo(
            name=response.get('Name'),
            date=response.get('CreateDateText'),
            address=response.get('Address'),
            photo_url=response.get('PhotoURL'),
            distance=response.get('Distance'),
            location=Location(
                longitude=coordinates.get('Longitude'),
                latitude=coordinates.get('Latitude')
            )
        )

    objects = list(map(parse, data))

    return objects[0]
