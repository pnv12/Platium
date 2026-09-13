import hashlib
import os

from PIL import Image

from platium.core.result import ScanResult, ScanStatus


def _sha256_file(file_path, chunk_size=1024 * 1024):
    """Calculate SHA-256 hash for the image file."""
    digest = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)

    return digest.hexdigest()


def _average_hash(image):
    """Calculate a simple perceptual average hash."""
    grayscale = image.convert("L").resize((8, 8))
    pixels = list(grayscale.getdata())
    average = sum(pixels) / len(pixels)

    return "".join("1" if pixel >= average else "0" for pixel in pixels)


def search(image_path, verbose=False) -> ScanResult:
    """
    Analyze an image and return structured Image Intelligence data.

    Current analysis:
    - file validation
    - image format
    - dimensions
    - mode
    - file size
    - SHA-256 hash
    - perceptual average hash
    """

    if not image_path:
        return ScanResult.error_result(
            target=image_path,
            scanner="image",
            error="Image path is required"
        )

    if not os.path.isfile(image_path):
        return ScanResult.error_result(
            target=image_path,
            scanner="image",
            error=f"File not found: {image_path}"
        )

    try:
        file_size = os.path.getsize(image_path)

        with Image.open(image_path) as image:
            image_format = image.format
            width, height = image.size
            mode = image.mode
            average_hash = _average_hash(image)

        sha256 = _sha256_file(image_path)

        result_data = {
            "file": {
                "path": os.path.abspath(image_path),
                "name": os.path.basename(image_path),
                "size": file_size
            },
            "image": {
                "format": image_format,
                "width": width,
                "height": height,
                "mode": mode,
                "aspect_ratio": round(width / height, 6) if height else None
            },
            "fingerprint": {
                "sha256": sha256,
                "average_hash": average_hash
            }
        }

        sources = {
            "image": {
                "status": "success",
                "message": "Image analyzed successfully"
            },
            "hash": {
                "status": "success",
                "algorithms": ["sha256", "average_hash"]
            }
        }

        evidence = [
            "Image file validated",
            f"Image format: {image_format}",
            f"Image dimensions: {width}x{height}",
            "SHA-256 fingerprint calculated",
            "Perceptual average hash calculated"
        ]

        return ScanResult(
            target=image_path,
            scanner="image",
            status=ScanStatus.SUCCESS,
            data=result_data,
            sources=sources,
            confidence=0.95,
            evidence=evidence
        )

    except (OSError, ValueError) as exc:
        return ScanResult.error_result(
            target=image_path,
            scanner="image",
            error=str(exc)
        )

    except Exception as exc:
        return ScanResult.error_result(
            target=image_path,
            scanner="image",
            error=str(exc)
      )
