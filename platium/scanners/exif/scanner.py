from PIL import Image
from PIL.ExifTags import TAGS
from platium.core.errors import ScannerError

def search(image_path, config=None, verbose=False):
    """
    Витягує EXIF-дані з фотографії.
    """
    results = {
        "target": image_path,
        "scan_type": "exif",
        "status": "error",
        "data": {}
    }
    
    try:
        image = Image.open(image_path)
        exifdata = image.getexif()
        if not exifdata:
            results["status"] = "no_exif"
            results["error"] = "No EXIF data found"
            return results
        
        for tag_id, value in exifdata.items():
            tag = TAGS.get(tag_id, tag_id)
            results["data"][tag] = str(value)
        
        results["status"] = "success"
        
    except FileNotFoundError:
        results["status"] = "error"
        results["error"] = f"File not found: {image_path}"
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    return results
