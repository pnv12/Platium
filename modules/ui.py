"""
UI Module — Інтерфейс для Platium
"""

import os
import sys
import time

def display_banner():
    """Головний баннер з ефектом матриці"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║    ██████╗ ██╗     █████╗ ████████╗██╗██╗   ██╗███╗   ███╗              ║
    ║    ██╔══██╗██║    ██╔══██╗╚══██╔══╝██║██║   ██║████╗ ████║              ║
    ║    ██████╔╝██║    ███████║   ██║   ██║██║   ██║██╔████╔██║              ║
    ║    ██╔═══╝ ██║    ██╔══██║   ██║   ██║██║   ██║██║╚██╔╝██║              ║
    ║    ██║     ███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚═╝ ██║              ║
    ║    ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝     ╚═╝              ║
    ║                                                                          ║
    ║    ██████╗ ███████╗██╗     ███████╗ █████╗ ███████╗███████╗              ║
    ║    ██╔══██╗██╔════╝██║     ██╔════╝██╔══██╗██╔════╝██╔════╝              ║
    ║    ██████╔╝█████╗  ██║     █████╗  ███████║███████╗███████╗              ║
    ║    ██╔══██╗██╔══╝  ██║     ██╔══╝  ██╔══██║╚════██║╚════██║              ║
    ║    ██║  ██║███████╗███████╗███████╗██║  ██║███████║███████║              ║
    ║    ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝              ║
    ║                                                                          ║
    ║    🚀 ADVANCED OSINT FRAMEWORK v4.0                                     ║
    ║    Author: Neo | Github: pnv21                                          ║
    ║    ══════════════════════════════════════════════════════════════════════║
    ║    [🔍] 60+ Platforms  |  [📧] Email Breaches  |  [🌐] Darknet          ║
    ║    [📱] Phone Analysis  |  [🌍] IP Geolocation  |  [🔗] Graph Analysis  ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    time.sleep(0.5)

def animate_loading():
    """Анімація завантаження (матричний стиль)"""
    animation = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    for i in range(3):
        for frame in animation:
            sys.stdout.write(f"\r   {frame} Збір даних...")
            sys.stdout.flush()
            time.sleep(0.05)
    sys.stdout.write("\r   ✅ Готово!            \n")

def progress_bar(current, total, label):
    """Прогрес-бар з кольором"""
    percent = (current / total) * 100
    bar_length = 30
    filled = int(bar_length * current // total)
    bar = '█' * filled + '░' * (bar_length - filled)
    color = "\033[92m" if percent > 50 else "\033[93m"
    reset = "\033[0m"
    sys.stdout.write(f"\r   [{color}{bar}{reset}] {percent:.0f}% - {label} ")
    sys.stdout.flush()
    if current == total:
        sys.stdout.write("✅\n")

def print_header(text):
    """Друк заголовка"""
    print("\n" + "="*60)
    print(f"   {text}")
    print("="*60)

def cyber_menu():
    """Інтерактивне меню в стилі кіберпанк"""
    os.system('cls' if os.name == 'nt' else 'clear')
    display_banner()
    
    menu = """
    ╔══════════════════════════════════════╗
    ║        🎯 ГОЛОВНЕ МЕНЮ              ║
    ╠══════════════════════════════════════╣
    ║  1. Пошук за нікнеймом              ║
    ║  2. Пошук за email                  ║
    ║  3. Аналіз номеру телефону          ║
    ║  4. Аналіз IP-адреси               ║
    ║  5. EXIF-аналіз фото               ║
    ║  6. Аналіз соцмереж                ║
    ║  7. Пошук у даркнеті               ║
    ║  8. Побудова графу зв'язків        ║
    ║  9. Перевірка загроз               ║
    ║  0. Вихід                          ║
    ╚══════════════════════════════════════╝
    """
    print(menu)
    
    while True:
        choice = input("\n🔐 Введіть номер модуля: ")
        if choice == "0":
            print("🔒 Завершення роботи...")
            sys.exit(0)
        elif choice == "1":
            username = input("Введіть нікнейм: ")
            print(f"\n🔍 Пошук за нікнеймом: {username}")
            animate_loading()
            result = username_scanner.search(username)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "2":
            email = input("Введіть email: ")
            print(f"\n📧 Пошук за email: {email}")
            animate_loading()
            result = email_scanner.search(email)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "3":
            phone = input("Введіть номер телефону: ")
            print(f"\n📱 Аналіз номеру: {phone}")
            animate_loading()
            result = phone_scanner.search(phone)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "4":
            ip = input("Введіть IP-адресу: ")
            print(f"\n🌍 Аналіз IP: {ip}")
            animate_loading()
            result = ip_scanner.search(ip)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "5":
            path = input("Введіть шлях до фото: ")
            print(f"\n🖼️ EXIF-аналіз: {path}")
            animate_loading()
            result = exif_extractor.extract(path)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "6":
            social = input("Введіть нік у соцмережі: ")
            print(f"\n📊 Аналіз соцмереж: {social}")
            animate_loading()
            result = social_analyzer.search(social)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "7":
            query = input("Введіть запит для даркнету: ")
            print(f"\n🌐 Пошук у даркнеті: {query}")
            animate_loading()
            result = darknet_scanner.search(query)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "8":
            email_graph = input("Введіть email для побудови графу: ")
            print(f"\n🔗 Побудова графу зв'язків: {email_graph}")
            animate_loading()
            result = graph_builder.build(email_graph)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "9":
            threat = input("Введіть email/IP для перевірки загроз: ")
            print(f"\n🛡️ Перевірка загроз: {threat}")
            animate_loading()
            result = threat_intel.check(threat)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ Невірний вибір. Спробуйте ще раз.")
        
        input("\nНатисніть Enter для продовження...")
        os.system('cls' if os.name == 'nt' else 'clear')
        print(menu)
