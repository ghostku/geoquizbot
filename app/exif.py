# pylint: disable=bad-continuation, protected-access, no-self-use

"""Библиотека для извлечения Geo-данных из EXIF."""
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


class ImageMetaData:
    """
    Extract the exif data from any image.

    Data includes GPS coordinates, Focal Length, Manufacture, and more.
    """

    exif_data = None
    image = None

    def __init__(self, img_path: str) -> None:
        self.image = Image.open(img_path)
        self.get_exif_data()
        super(ImageMetaData, self).__init__()

    def get_exif_data(self) -> dict:
        """
        Return a dictionary from the exif data of an PIL Image item.

        Also converts the GPS Tags
        """
        exif_data = {}
        info = self.image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for item in value:
                        sub_decoded = GPSTAGS.get(item, item)
                        gps_data[sub_decoded] = value[item]

                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value
        self.exif_data = exif_data
        return exif_data

    def convert_to_degress(self, value: tuple) -> float:
        """Convert the GPS coordinates stored in the EXIF to degress in float format."""

        def convert_part(value: tuple) -> float:
            if isinstance(value, tuple):
                result = float(value[0]) / float(value[1])
            else:
                return float(value)
            return result

        deg = convert_part(value[0])
        minute = convert_part(value[1])
        sec = convert_part(value[2])
        return deg + (minute / 60.0) + (sec / 3600.0)

    def get_lat_lng(self) -> tuple:
        """Return the latitude and longitude.

        If available, from the provided exif_data (obtained through get_exif_data above)
        """
        lat = None
        lng = None
        exif_data = self.get_exif_data()
        if "GPSInfo" in exif_data:
            gps_info = exif_data["GPSInfo"]
            gps_latitude = gps_info.get("GPSLatitude", None)
            gps_latitude_ref = gps_info.get("GPSLatitudeRef", None)
            gps_longitude = gps_info.get("GPSLongitude", None)
            gps_longitude_ref = gps_info.get("GPSLongitudeRef", None)
            if all([gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref]):
                lat = self.convert_to_degress(gps_latitude)
                if gps_latitude_ref != "N":
                    lat = 0 - lat
                lng = self.convert_to_degress(gps_longitude)
                if gps_longitude_ref != "E":
                    lng = 0 - lng
        return lat, lng
