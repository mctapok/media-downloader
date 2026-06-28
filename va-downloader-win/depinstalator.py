import subprocess
import sys
import os
import urllib.request
import shutil
import zipfile
import time

# Фикс кодировки Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

try:
    import requests
except ImportError:
    print("[•] Установка requests...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "requests"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    import requests

def print_status(message):
    print(f"[•] {message}")

def install_package(package_name):
    """Установка pip-пакета"""
    print_status(f"Установка {package_name}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=180
        )
        if result.returncode == 0:
            return True, f"{package_name} установлен"
        else:
            err = result.stderr.strip().split('\n')[-2:]
            print(f"  [!] {chr(10).join(err)}")
            return False, f"Ошибка установки {package_name}"
    except subprocess.TimeoutExpired:
        return False, "Таймаут (проверьте интернет)"
    except Exception as e:
        return False, f"Ошибка: {e}"

def check_ffmpeg():
    """Проверка наличия ffmpeg"""
    print_status("Проверка ffmpeg...")
    if shutil.which("ffmpeg"):
        return True, "ffmpeg найден в PATH"
    local = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
    if os.path.exists(local):
        return True, "ffmpeg найден локально"
    return False, "ffmpeg не найден"

def download_ffmpeg():
    """Скачивание и распаковка ffmpeg"""
    print_status("Скачивание ffmpeg...")
    
    # Проверяем, есть ли requests
    try:
        import requests
    except ImportError:
        print_status("Установка requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import requests
    
    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg")
    if os.path.exists(ffmpeg_dir):
        shutil.rmtree(ffmpeg_dir)
    os.makedirs(ffmpeg_dir)
    
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    archive = os.path.join(ffmpeg_dir, "ffmpeg.zip")

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    try:
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
    
            # Получаем размер из заголовков (в байтах)
        total_size_bytes = r.headers.get('content-length')
            
        if total_size_bytes is not None:
            total_size_mb = int(total_size_bytes) / (1024 * 1024)

        print_status(f"Загрузка архива {total_size_mb} mb...")
        
   
        
        
        for attempt in range(1, 4):
            try:
                with requests.get(url, headers=headers, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    
                    total = int(r.headers.get('Content-Length', 0))
                    downloaded = 0
                    
                    with open(archive, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                percent = downloaded * 100 // total
                                mb_down = downloaded / (1024 * 1024)
                                mb_total = total / (1024 * 1024)
                                print(f"\r  Загрузка: {percent}% ({mb_down:.1f}/{mb_total:.1f} MB)", end='')
                print()  # Перенос строки после прогресса
                break
            except Exception as e:
                if attempt < 3:
                    print(f"\n  [!] Попытка {attempt} не удалась ({e}), пробуем снова...")
                    time.sleep(2)
                else:
                    raise e
        
        # Проверяем целостность
        size_mb = os.path.getsize(archive) / (1024 * 1024)
        if size_mb < 5:
            os.remove(archive)
            return False, f"Архив повреждён (размер: {size_mb:.1f} MB)"
        print_status(f"Загружено: {size_mb:.1f} MB")
        
        print_status("Распаковка...")
        with zipfile.ZipFile(archive, 'r') as z:
            z.extractall(ffmpeg_dir)
        
        # Ищем bin с ffmpeg.exe
        bin_dir = None
        for root, dirs, files in os.walk(ffmpeg_dir):
            if "ffmpeg.exe" in files:
                bin_dir = root
                break
        
        if not bin_dir:
            return False, "ffmpeg.exe не найден в архиве"
        
        # Перемещаем в ffmpeg/bin
        target_bin = os.path.join(ffmpeg_dir, "bin")
        if os.path.exists(target_bin):
            shutil.rmtree(target_bin)
        
        if os.path.normpath(bin_dir) != os.path.normpath(target_bin):
            shutil.move(bin_dir, target_bin)
        
        # Чистим
        os.remove(archive)
        
        # Удаляем лишние папки
        for item in os.listdir(ffmpeg_dir):
            item_path = os.path.join(ffmpeg_dir, item)
            if item != "bin" and os.path.isdir(item_path):
                shutil.rmtree(item_path, ignore_errors=True)
        
        # Добавляем в PATH текущей сессии
        os.environ["PATH"] = target_bin + os.pathsep + os.environ.get("PATH", "")
        
        return True, "ffmpeg установлен локально"
        
    except Exception as e:
        return False, f"Ошибка: {e}"

def add_to_system_path(ffmpeg_bin):
    """Добавление в пользовательский PATH через реестр"""
    print_status("Добавление в PATH...")
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ | winreg.KEY_SET_VALUE
        )
        current_path, _ = winreg.QueryValueEx(key, "PATH")
        
        if ffmpeg_bin not in current_path:
            new_path = current_path + os.pathsep + ffmpeg_bin
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            print_status("PATH обновлён в реестре")
        else:
            print_status("Путь уже есть в PATH")
        
        winreg.CloseKey(key)
    except Exception as e:
        print(f"  [!] Не удалось обновить PATH: {e}")
        print(f"  [!] Добавьте папку вручную: {ffmpeg_bin}")

def main():
    print("=" * 60)
    print("  УСТАНОВЩИК ЗАВИСИМОСТЕЙ")
    print("=" * 60)
    print()
    
    # Python
    v = sys.version_info
    print(f"  {'✅' if v >= (3, 7) else '❌'} Python {v.major}.{v.minor}")
    
    # yt-dlp
    try:
        import yt_dlp
        print(f"  ✅ yt-dlp v{yt_dlp.version.__version__}")
    except ImportError:
        ok, msg = install_package("yt-dlp")
        print(f"  {'✅' if ok else '❌'} {msg}")
    
    # ffmpeg
    ok, msg = check_ffmpeg()
    print(f"  {'✅' if ok else '❌'} {msg}")
    
    if not ok:
        print()
        choice = input("Скачать ffmpeg? (Y/N): ").strip().lower()
        if choice in ['y', 'yes', '']:
            ok, msg = download_ffmpeg()
            print(f"  {'✅' if ok else '❌'} {msg}")
            if ok:
                ffmpeg_bin = os.path.join(os.getcwd(), "ffmpeg", "bin")
                add_to_system_path(ffmpeg_bin)
    
    # Итог
    print()
    print("=" * 60)
    
    ffmpeg_ok = shutil.which("ffmpeg") or os.path.exists(
        os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
    )
    
    try:
        import yt_dlp
        yt_ok = True
    except ImportError:
        yt_ok = False
    
    if yt_ok and ffmpeg_ok:
        print("  ✅ ВСЁ ГОТОВО К РАБОТЕ")
    else:
        if not yt_ok:
            print("  ❌ yt-dlp не установлен")
        if not ffmpeg_ok:
            print("  ⚠️ ffmpeg не установлен (MP3/Full HD недоступны)")
    
    print("=" * 60)
    print()
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()