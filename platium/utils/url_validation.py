import ipaddress
import re
from urllib.parse import urlparse

# Приватні та локальні діапазони IP-адрес
PRIVATE_IP_RANGES = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('169.254.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('0.0.0.0/8'),
]

def is_private_ip(ip_str: str) -> bool:
    """Перевіряє, чи IP-адреса є приватною або локальною."""
    try:
        ip = ipaddress.ip_address(ip_str)
        for network in PRIVATE_IP_RANGES:
            if ip in network:
                return True
        return False
    except ValueError:
        return True  # Якщо не вдалося розпізнати IP, вважаємо його небезпечним

def is_safe_url(url: str) -> bool:
    """
    Перевіряє, чи URL-адреса безпечна для запиту.
    Повертає True, якщо URL веде на публічний IP.
    """
    if not url:
        return False

    parsed = urlparse(url)
    if not parsed.netloc:
        return False

    # Спроба отримати IP-адресу з хоста
    host = parsed.netloc.split(':')[0]
    try:
        # Якщо це доменне ім'я, резолвимо його в IP
        import socket
        ip = socket.gethostbyname(host)
        return not is_private_ip(ip)
    except socket.gaierror:
        # Якщо не вдалося резолвити, вважаємо небезпечним
        return False
