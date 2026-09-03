from PIL import Image
from PIL.ExifTags import TAGS
from platium.core.config import load_config
from platium.core.errors import ScannerError

def search(image_path, config=None, verbose=False):
    if config is None:
        config = load_config()
    
    results = {
        "target": image_path,
        "scan_type": "exif",
        "sources": {}
    }
    
    try:
        image = Image.open(image_path)
        exifdata = image.getexif()
        if not exifdata:
            results["status"] = "no_exif"
            results["message"] = "No EXIF data found"
            return results
        
        exif_dict = {}
        for tag_id, value in exifdata.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_dict[tag] = str(value)
        
        results["sources"]["exif"] = {
            "status": "success",
            "data": exif_dict
        }
        results["status"] = "success"
        
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    return results
