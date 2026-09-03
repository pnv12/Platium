import json

def display_banner():
    banner = """
    ╔══════════════════════════════════════╗
    ║          PLATIUM v0.1                       ║
    ║    Advanced OSINT Framework                 ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

def print_result(data, scan_type):
    print(f"\n[+] Results for {scan_type}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
