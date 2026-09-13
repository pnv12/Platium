from PIL.ExifTags import TAGS


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
            "gps_present": False
        }

    fields = {}

    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, str(tag_id))

        try:
            fields[tag_name] = str(value)
        except Exception:
            fields[tag_name] = repr(value)

    return {
        "available": True,
        "fields": fields,
        "gps_present": "GPSInfo" in fields
    }
