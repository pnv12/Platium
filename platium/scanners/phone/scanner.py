import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from platium.core.result import ScanResult, ScanStatus
from platium.core.config import config

def search(phone, verbose=False) -> ScanResult:
    """
    Аналізує номер телефону.
    Повертає ScanResult.
    """
    sources = {}
    data = {}
    errors = []
    status = ScanStatus.NOT_FOUND

    try:
        number = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(number):
            return ScanResult(
                target=phone,
                scanner="phone",
                status=ScanStatus.INVALID,
                error="Invalid phone number"
            )

        data["country"] = geocoder.description_for_number(number, "en")
        data["operator"] = carrier.name_for_number(number, "en")
        data["timezone"] = timezone.time_zones_for_number(number)

        sources["phonenumbers"] = {"status": "success", "data": data}
        status = ScanStatus.SUCCESS

    except phonenumbers.NumberParseException as e:
        return ScanResult.error_result(
            target=phone,
            scanner="phone",
            error=str(e)
        )
    except Exception as e:
        return ScanResult.error_result(
            target=phone,
            scanner="phone",
            error=str(e)
        )

    return ScanResult(
        target=phone,
        scanner="phone",
        status=status,
        data=data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=0.95 if status == ScanStatus.SUCCESS else 0.0,
        evidence=[f"Country: {data.get('country')}", f"Operator: {data.get('operator')}"]
    )
