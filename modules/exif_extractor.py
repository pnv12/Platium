"""
EXIF Extractor — метадані з фото
"""

from PIL import Image
from PIL.ExifTags import TAGS

def extract(image_path):
    """Витягує EXIF-дані з фото"""
    results = {}
    try:
        image = Image.open(image_path)
        exifdata = image.getexif()
        if not exifdata:
            results["error"] = "EXIF-дані не знайдено"
            return results
        
        for tag_id, value in exifdata.items():
            tag = TAGS.get(tag_id, tag_id)
            results[tag] = str(value)
            
    except Exception as e:
        results["error"] = str(e)
    
    return results
