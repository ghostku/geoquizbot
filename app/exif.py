# pylint: disable=bad-continuation, protected-access, no-self-use

"""Библиотека для извлечения Geo-данных из EXIF
"""
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


class ImageMetaData:
    """
    Extract the exif data from any image. Data includes GPS coordinates,
    Focal Length, Manufacture, and more.
    """

    exif_data = None
    image = None

    def __init__(self, img_path):
        self.image = Image.open(img_path)
        self.get_exif_data()
        super(ImageMetaData, self).__init__()

    def get_exif_data(self):
        """
        Returns a dictionary from the exif data of an
        PIL Image item. Also converts the GPS Tags
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

    def convert_to_degress(self, value):
        """
        Helper function to convert the GPS coordinates
        stored in the EXIF to degress in float format
        """  # noqa
        deg0 = value[0][0]
        deg1 = value[0][1]
        deg = float(deg0) / float(deg1)

        min0 = value[1][0]
        min1 = value[1][1]
        minute = float(min0) / float(min1)

        sec0 = value[2][0]
        sec1 = value[2][1]
        sec = float(sec0) / float(sec1)

        return deg + (minute / 60.0) + (sec / 3600.0)

    def get_lat_lng(self):
        """
        Returns the latitude and longitude, if available,
        from the provided exif_data (obtained through get_exif_data above)
        """  # noqa
        lat = None
        lng = None
        exif_data = self.get_exif_data()
        # print(exif_data)
        if "GPSInfo" in exif_data:
            gps_info = exif_data["GPSInfo"]
            gps_latitude = gps_info.get("GPSLatitude", None)
            gps_latitude_ref = gps_info.get("GPSLatitudeRef", None)
            gps_longitude = gps_info.get("GPSLongitude", None)
            gps_longitude_ref = gps_info.get("GPSLongitudeRef", None)
            if (
                gps_latitude
                and gps_latitude_ref
                and gps_longitude
                and gps_longitude_ref
            ):
                lat = self.convert_to_degress(gps_latitude)
                if gps_latitude_ref != "N":
                    lat = 0 - lat
                lng = self.convert_to_degress(gps_longitude)
                if gps_longitude_ref != "E":
                    lng = 0 - lng
        return lat, lng
