from PIL.ExifTags import GPSTAGS, TAGS


def _convert_gps_coordinate(value):
    """Convert a GPS EXIF coordinate into decimal degrees."""
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        return None

    try:
        degrees, minutes, seconds = value

        def to_float(item):
            if hasattr(item, "numerator") and hasattr(item, "denominator"):
                if item.denominator == 0:
                    raise ValueError
                return float(item.numerator) / float(item.denominator)

            if isinstance(item, (tuple, list)) and len(item) == 2:
                numerator, denominator = item
                if denominator == 0:
                    raise ValueError
                return float(numerator) / float(denominator)

            return float(item)

        degrees = to_float(degrees)
        minutes = to_float(minutes)
        seconds = to_float(seconds)

        return degrees + (minutes / 60.0) + (seconds / 3600.0)

    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _extract_gps(exif_data):
    """Extract normalized GPS metadata from EXIF."""
    try:
        gps_ifd = exif_data.get_ifd(0x8825)
    except (AttributeError, KeyError, TypeError, ValueError):
        return {
            "present": False,
            "latitude": None,
            "longitude": None,
            "latitude_ref": None,
            "longitude_ref": None
        }

    if not gps_ifd:
        return {
            "present": False,
            "latitude": None,
            "longitude": None,
            "latitude_ref": None,
            "longitude_ref": None
        }

    gps = {}

    for tag_id, value in gps_ifd.items():
        tag_name = GPSTAGS.get(
            tag_id,
            str(tag_id)
        )
        gps[tag_name] = value

    latitude = _convert_gps_coordinate(
        gps.get("GPSLatitude")
    )
    longitude = _convert_gps_coordinate(
        gps.get("GPSLongitude")
    )

    latitude_ref = gps.get("GPSLatitudeRef")
    longitude_ref = gps.get("GPSLongitudeRef")

    if isinstance(latitude_ref, bytes):
        latitude_ref = latitude_ref.decode(
            "utf-8",
            errors="ignore"
        )

    if isinstance(longitude_ref, bytes):
        longitude_ref = longitude_ref.decode(
            "utf-8",
            errors="ignore"
        )

    if latitude is not None and latitude_ref == "S":
        latitude = -latitude

    if longitude is not None and longitude_ref == "W":
        longitude = -longitude

    return {
        "present": True,
        "latitude": latitude,
        "longitude": longitude,
        "latitude_ref": latitude_ref,
        "longitude_ref": longitude_ref
    }


def extract_exif(image):
    """
    Extract normalized EXIF metadata from an opened PIL image.

    Returns a JSON-safe dictionary suitable for ScanResult.data.
    """
    exif_data = image.getexif()

    if not exif_data:
        return {
            "available": False,
            "fields": {},
            "gps_present": False,
            "gps": {
                "present": False,
                "latitude": None,
                "longitude": None,
                "latitude_ref": None,
                "longitude_ref": None
            }
        }

    fields = {}

    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(
            tag_id,
            str(tag_id)
        )

        if tag_name == "GPSInfo":
            continue

        try:
            fields[tag_name] = str(value)
        except Exception:
            fields[tag_name] = repr(value)

    gps = _extract_gps(exif_data)

    return {
        "available": True,
        "fields": fields,
        "gps_present": gps["present"],
        "gps": gps
    }
