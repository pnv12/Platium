# Platium

**Platium** — це легкий, але потужний OSINT-фреймворк для дослідників, журналістів та спеціалістів з кібербезпеки. Він збирає публічну інформацію з відкритих джерел, аналізує зв’язки та генерує структуровані звіти.

> **Поточний статус:** `Beta` — стабільна версія, активно тестується.  
> **Мова:** Python 3.8+  
> **Ліцензія:** MIT

---

## 🚀 Швидкий старт (Quick Start)

```bash
# Клонування репозиторію
git clone https://github.com/pnv12/Platium.git
cd Platium

# Встановлення залежностей
pip install -r requirements.txt

# Швидкий приклад
python platium.py --deep pnv21 --aggregate
```

---

## ✨ Основні можливості (Features)

| Модуль | Опис | Реальних джерел |
|--------|------|----------------|
| **Username Scanner** | Пошук нікнейму на 80+ платформах | 25 перевірених (GitHub, Twitter, IG, VK, Reddit, YouTube, TikTok, Telegram, Steam, Spotify, Snapchat, Pinterest, Flickr, Vimeo, Twitch, SoundCloud, Patreon, GitLab, Bitbucket, Gravatar, HackerNews, ProductHunt, Keybase, Pastebin, Replit, Dev.to) |
| **Email Scanner** | Перевірка email на витік даних через HIBP та LeakCheck | 2 API |
| **Phone Analyzer** | Визначення країни, оператора, часового поясу | Без зовнішніх API |
| **IP Scanner** | Геолокація, whois, визначення проксі/VPN | 3 джерела (ip-api, ipinfo, whois) |
| **EXIF Extractor** | Витягування метаданих з фото (GPS, камера, дата) | Локально |
| **Social Analyzer** | Аналіз профілів у соцмережах (Twitter, Instagram) | Публічні сторінки |
| **Darknet Scanner** | Пошук у даркнеті через Ahmia (з підтримкою Tor) | 1 пошуковик |
| **Graph Builder** | Побудова графу зв'язків на основі email/ніка | Внутрішня логіка |
| **Threat Intelligence** | Перевірка IP/доменів через VirusTotal, AbuseIPDB, Shodan | 3 API |
| **Report Generator** | Генерація звітів у TXT, JSON, HTML | Вбудовано |
| **Data Aggregator** | Локальна база даних (SQLite) для збереження історії пошуків та виявлення зв'язків | Вбудовано |
| **Deep OSINT** | Комбінований глибокий пошук за будь-яким типом запиту (email, номер, IP, нік, домен) | Вбудовано |

---

## 📦 Встановлення (Installation)

### Вимоги (Requirements)
- Python 3.8 або новіший
- pip
- (опціонально) Tor для даркнет-скану

### Кроки
```bash
git clone https://github.com/pnv12/Platium.git
cd Platium
pip install -r requirements.txt
```

---

## 🛠️ Конфігурація (Configuration)

Для роботи деяких модулів потрібні API-ключі. Створи файл `.env` (або `config.py`) і додай свої ключі за зразком:

```bash
# .env.example
SHODAN_API_KEY=your_shodan_key
VIRUSTOTAL_API_KEY=your_vt_key
ABUSEIPDB_API_KEY=your_abuseipdb_key
IPINFO_API_KEY=your_ipinfo_key
NUMVERIFY_API_KEY=your_numverify_key
SECURITYTRAILS_API_KEY=your_st_key
```

**Важливо:** ніколи не комити цей файл у репозиторій. Він має бути в `.gitignore`.

---

## 🎯 Використання (Usage)

### Базові команди (CLI)

```bash
# Пошук за нікнеймом
python platium.py --username pnv21

# Пошук за email
python platium.py --email test@example.com

# Аналіз номеру телефону
python platium.py --phone +380991234567

# Аналіз IP
python platium.py --ip 8.8.8.8

# Глибокий OSINT (автовизначення типу)
python platium.py --deep pnv21

# Зберегти результат у базу
python platium.py --deep pnv21 --aggregate

# Знайти зв'язки для запиту
python platium.py --connections pnv21

# Переглянути аналітику накопичених даних
python platium.py --analyze
```

### Інтерактивне меню
```bash
python platium.py --menu
```

### Демонстрація
```bash
python platium.py --demo
```

### Приклад виводу
```
[+] GitHub       Found → https://github.com/pnv21
[+] Reddit       Found → https://reddit.com/user/pnv21
[!] Instagram    Rate limited (try again later)
[-] Twitter      Not found
```

---

## 🧪 Тестування (Testing)

Проект має базові тести (розширюються). Запуск:
```bash
pytest tests/
```

---

## 🛡️ Безпека та відповідальне використання (Security & Responsible Use)

- Platium **не зберігає** жодних даних на зовнішніх серверах.
- Усі API-ключі зберігаються локально і нікуди не передаються.
- Інструмент призначений **виключно для освітніх цілей** та аналізу публічно доступної інформації.
- Заборонено використовувати для переслідування, крадіжки облікових даних або будь-яких незаконних дій.
- Користувач несе повну відповідальність за використання цього програмного забезпечення.

---

## 📂 Структура проєкту (Architecture)

```
Platium/
├── platium.py                # Точка входу (CLI)
├── modules/                  # Всі модулі
│   ├── deep_osint.py
│   ├── data_aggregator.py
│   ├── username_scanner.py
│   ├── email_scanner.py
│   ├── phone_scanner.py
│   ├── ip_scanner.py
│   ├── exif_extractor.py
│   ├── social_analyzer.py
│   ├── darknet_scanner.py
│   ├── graph_builder.py
│   ├── threat_intel.py
│   ├── report_generator.py
│   ├── ui.py
│   └── utils.py
├── data/                     # Локальні дані
│   ├── reports/              # Згенеровані звіти
│   └── platium.db            # SQLite-база
├── tests/                    # Модульні тести (в розробці)
├── docs/                     # Документація (в розробці)
├── .github/workflows/        # CI/CD (в розробці)
├── .env.example              # Шаблон для API-ключів
├── requirements.txt          # Залежності
├── LICENSE                   # MIT
└── README.md                 # Цей файл
```

---

## 🗺️ Подальший розвиток (Roadmap)

- [ ] Додати більше джерел для нікнеймів (до 100+).
- [ ] Інтеграція з AI для аналізу зв’язків.
- [ ] Веб-інтерфейс (Flask/Django).
- [ ] Підтримка Docker.
- [ ] Автоматичне тестування та CI/CD (GitHub Actions).
- [ ] Додаткові сканери (BreachDB, Pastebin тощо).

---

## 🤝 Внесок (Contributing)

Якщо ви хочете допомогти — відкривайте Issue або Pull Request. Будь-які покращення вітаються.

---

## 📜 Ліцензія

MIT License — вільне використання, модифікація та розповсюдження.

---

## 👤 Автор

**Neo** (pnv12)  
[GitHub](https://github.com/pnv12) · [Telegram](https://t.me/pnv21)

---

## ⭐ Підтримати проєкт

Якщо вам сподобався Platium — поставте зірочку на GitHub. Це допоможе проєкту розвиватися.

---

**Останнє оновлення:** 2 вересня 2026
