import os
from PIL import Image
from PIL.ExifTags import TAGS
from platium.core.result import ScanResult, ScanStatus
from platium.core.config import config

def search(image_path, verbose=False) -> ScanResult:
    """
    Витягує EXIF-метадані з зображення.
    Повертає ScanResult.
    """
    result_data = {}
    sources = {}
    errors = []
    status = ScanStatus.NOT_FOUND

    if not os.path.exists(image_path):
        return ScanResult.error_result(
            target=image_path,
            scanner="exif",
            error=f"File not found: {image_path}"
        )

    try:
        image = Image.open(image_path)
        exifdata = image.getexif()
        if not exifdata:
            sources["exif"] = {"status": "not_found", "message": "No EXIF data found"}
            return ScanResult(
                target=image_path,
                scanner="exif",
                status=ScanStatus.NOT_FOUND,
                sources=sources,
                error="No EXIF data found"
            )

        for tag_id, value in exifdata.items():
            tag_name = TAGS.get(tag_id, tag_id)
            result_data[tag_name] = str(value)

        sources["exif"] = {"status": "success", "count": len(result_data)}
        status = ScanStatus.SUCCESS

        # Додаємо GPS як окремий доказ, якщо є
        if "GPSInfo" in result_data:
            sources["gps"] = {"status": "found", "evidence": "GPS coordinates present"}

    except Exception as e:
        return ScanResult.error_result(
            target=image_path,
            scanner="exif",
            error=str(e)
        )

    return ScanResult(
        target=image_path,
        scanner="exif",
        status=status,
        data=result_data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=0.9 if status == ScanStatus.SUCCESS else 0.1,
        evidence=["EXIF data extracted"] if result_data else []
    )
