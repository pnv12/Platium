import os
import sys
import time
import json

# ------ ЦВЕТА ДЛЯ ТЕРМИНАЛА ------
COLORS = {
    "info": "\033[94m",
    "success": "\033[92m",
    "warning": "\033[93m",
    "error": "\033[91m",
    "reset": "\033[0m"
}

def print_status(message, status="info"):
    """Друк статусу з кольором"""
    color = COLORS.get(status, COLORS["info"])
    print(f"{color}[{status.upper()}]{COLORS['reset']} {message}")

def print_banner():
    """Головний баннер з ефектом матрицы"""
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                                         ║
    ║    ██████╗ ██╗     █████╗ ████████╗██╗██╗   ██╗███╗   ███╗                      ║
    ║    ██╔══██╗██║    ██╔══██╗╚══██╔══╝██║██║   ██║████╗ ████║                     ║
    ║    ██████╔╝██║    ███████║   ██║   ██║██║   ██║██╔████╔██║                      ║
    ║    ██╔═══╝ ██║    ██╔══██║   ██║   ██║██║   ██║██║╚██╔╝██║                      ║
    ║    ██║     ███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚═╝ ██║                     ║
    ║    ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝     ╚═╝                      ║
    ║                                                                                         ║
    ║    ██████╗ ███████╗██╗     ███████╗ █████╗ ███████╗███████╗                    ║
    ║    ██╔══██╗██╔════╝██║     ██╔════╝██╔══██╗██╔════╝██╔════╝                   ║
    ║    ██████╔╝█████╗  ██║     █████╗  ███████║███████╗███████╗                    ║
    ║    ██╔══██╗██╔══╝  ██║     ██╔══╝  ██╔══██║╚════██║╚════██║                    ║
    ║    ██║  ██║███████╗███████╗███████╗██║  ██║███████║███████║                   ║
    ║    ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝                   ║
    ║                                                                                        ║
    ║    🚀 ADVANCED OSINT FRAMEWORK v4.0                                                    ║
    ║    Author: Neo | Github: pnv21                                                         ║
    ║    ══════════════════════════════════════════════════════════════════════║
    ║    [🔍] 60+ Platforms  |  [📧] Email Breaches  |  [🌐] Darknet                         ║
    ║    [📱] Phone Analysis  |  [🌍] IP Geolocation  |  [🔗] Graph Analysis                 ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    time.sleep(0.5)

def animate_loading():
    """Анімація завантаження (матричний стиль)"""
    animation = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    for _ in range(3):
        for frame in animation:
            sys.stdout.write(f"\r   {frame} Збір даних...")
            sys.stdout.flush()
            time.sleep(0.05)
    sys.stdout.write("\r   ✅ Готово!            \n")

def progress_bar(current, total, label):
    """Прогрес-бар з кольором"""
    if total == 0:
        return
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

def print_results(data):
    """Вивід результатів у форматованому вигляді"""
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТИ:")
    for key, value in data.items():
        print(f"\n🔹 {key.upper()}:")
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    print(f"   {k}: {json.dumps(v, ensure_ascii=False)[:200]}...")
                else:
                    print(f"   {k}: {v}")
        else:
            print(f"   {value}")
    print("="*60)

def cyber_menu(modules):
    """Інтерактивне меню в стилі кіберпанк"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    menu = """
    ╔══════════════════════════════════════╗
    ║        🎯 ГОЛОВНЕ МЕНЮ                      ║
    ╠══════════════════════════════════════╣
    ║  1. Пошук за нікнеймом                      ║
    ║  2. Пошук за email                          ║
    ║  3. Аналіз номеру телефону                  ║
    ║  4. Аналіз IP-адреси                        ║
    ║  5. EXIF-аналіз фото                        ║
    ║  6. Аналіз соцмереж                         ║
    ║  7. Пошук у даркнеті                        ║
    ║  8. Побудова графу зв'язків                 ║
    ║  9. Перевірка загроз                        ║
    ║  0. Вихід                                   ║
    ╚══════════════════════════════════════╝
    """
    print(menu)
    
    while True:
        choice = input("\n🔐 Введіть номер модуля: ").strip()
        if choice == "0":
            print("🔒 Завершення роботи...")
            sys.exit(0)
        elif choice in modules:
            return choice
        else:
            print_status("Невірний вибір. Спробуйте ще раз.", "error")
