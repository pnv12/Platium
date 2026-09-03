import re
import ipaddress
from .errors import ValidationError

def validate_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValidationError(f"Invalid email: {email}")

def validate_username(username):
    if len(username) < 2:
        raise ValidationError("Username too short")
    if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
        raise ValidationError("Invalid characters in username")

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise ValidationError(f"Invalid IP: {ip}")

def validate_phone(phone):
    import phonenumbers
    try:
        phonenumbers.parse(phone, None)
    except:
        raise ValidationError(f"Invalid phone: {phone}")
