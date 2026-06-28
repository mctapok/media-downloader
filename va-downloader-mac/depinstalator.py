#!/usr/bin/env python3
"""
Установщик зависимостей для Загрузчика медиа (macOS)
Запуск: python3 install_dependencies_mac.py
"""

import subprocess
import sys
import os
import shutil
import platform


def print_status(message):
    print(f"  {message}")


def print_header(text):
    print()
    print("=" * 55)
    print(f"  {text}")
    print("=" * 55)
    print()


def print_success(text):
    print(f"  ✅ {text}")


def print_error(text):
    print(f"  ❌ {text}")


def print_warning(text):
    print(f"  ⚠️  {text}")


def check_python():
    print_status("Проверка Python...")
    version = sys.version_info
    if version < (3, 7):
        print_error(f"Python {version.major}.{version.minor} — требуется 3.7+")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_pip():
    print_status("Проверка pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_success("pip работает")
        return True
    except:
        print_error("pip не найден")
        return False


def check_homebrew():
    print_status("Проверка Homebrew...")
    if shutil.which("brew"):
        print_success("Homebrew установлен")
        return True
    print_warning("Homebrew не найден")
    return False


def install_homebrew():
    print()
    print_header("УСТАНОВКА HOMEBREW")
    print("Homebrew — менеджер пакетов для macOS.")
    print("Без него нельзя установить ffmpeg.")
    print()
    choice = input("Установить Homebrew? (Y/N): ").strip().lower()

    if choice not in ['y', 'yes', 'д', 'да', '']:
        print_warning("Пропущено. MP3 и Full HD будут недоступны.")
        return False

    print_status("Установка Homebrew...")
    print("(потребуется ввести пароль администратора)")
    print()

    try:
        install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        subprocess.run(install_cmd, shell=True, check=True)

        # Определяем архитектуру и добавляем brew в PATH
        if platform.machine() == "arm64":
            brew_path = "/opt/homebrew/bin"
        else:
            brew_path = "/usr/local/bin"

        os.environ["PATH"] = f"{brew_path}:{os.environ.get('PATH', '')}"

        # Добавляем в .zshrc или .bash_profile
        shell_config = os.path.expanduser("~/.zshrc")
        if not os.path.exists(shell_config):
            shell_config = os.path.expanduser("~/.bash_profile")

        with open(shell_config, "a") as f:
            f.write(f'\n# Homebrew\neval "$({brew_path}/brew shellenv)"\n')

        print_success("Homebrew установлен")
        return True
    except:
        print_error("Не удалось установить Homebrew")
        return False


def install_ffmpeg():
    print()
    print_header("УСТАНОВКА FFMPEG")
    print("ffmpeg нужен для:")
    print("  • Видео в Full HD (1080p)")
    print("  • Конвертации в MP3")
    print()

    # Проверяем, есть ли уже
    if shutil.which("ffmpeg"):
        print_success("ffmpeg уже установлен")
        return True

    if not check_homebrew():
        if not install_homebrew():
            return False

    choice = input("Установить ffmpeg через Homebrew? (Y/N): ").strip().lower()
    if choice not in ['y', 'yes', 'д', 'да', '']:
        print_warning("Пропущено. MP3 и Full HD будут недоступны.")
        return False

    print_status("Установка ffmpeg...")
    try:
        subprocess.check_call(["brew", "install", "ffmpeg"])
        print_success("ffmpeg установлен")
        return True
    except:
        print_error("Не удалось установить ffmpeg")
        print("Попробуйте вручную: brew install ffmpeg")
        return False


def install_yt_dlp():
    print()
    print_header("УСТАНОВКА YT-DLP")

    # Проверяем, есть ли уже
    try:
        import yt_dlp
        print_success(f"yt-dlp уже установлен (v{yt_dlp.version.__version__})")
        return True
    except ImportError:
        pass

    print_status("Установка yt-dlp...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_success("yt-dlp установлен")
        return True
    except:
        print_error("Не удалось установить yt-dlp")
        print("Попробуйте вручную: pip3 install yt-dlp")
        return False


def check_all():
    """Проверка всех зависимостей (для --check-only)"""
    all_ok = True

    if not check_python():
        all_ok = False
    if not check_pip():
        all_ok = False

    try:
        import yt_dlp
        print_success(f"yt-dlp v{yt_dlp.version.__version__}")
    except ImportError:
        print_error("yt-dlp не установлен")
        all_ok = False

    if shutil.which("ffmpeg"):
        print_success("ffmpeg установлен")
    else:
        print_error("ffmpeg не установлен")
        all_ok = False

    return all_ok


def main():
    # Проверка аргументов
    if "--check-only" in sys.argv:
        print()
        print("=" * 55)
        print("  ПРОВЕРКА ЗАВИСИМОСТЕЙ")
        print("=" * 55)
        print()
        if check_all():
            print()
            print_success("Все зависимости установлены")
            sys.exit(0)
        else:
            print()
            print_error("Есть отсутствующие зависимости")
            sys.exit(1)

    print()
    print("=" * 55)
    print("  🍎 УСТАНОВЩИК ДЛЯ ЗАГРУЗЧИКА МЕДИА (macOS)")
    print("=" * 55)
    print()
    print("Этот скрипт проверит и установит всё необходимое:")
    print("  1. Python 3.7+")
    print("  2. pip (менеджер пакетов Python)")
    print("  3. Homebrew (менеджер пакетов macOS)")
    print("  4. ffmpeg (для Full HD и MP3)")
    print("  5. yt-dlp (библиотека загрузки)")
    print()
    input("Нажмите Enter для продолжения...")

    # Проверки
    if not check_python():
        print()
        print_error("Установите Python 3.7+ с python.org")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)

    if not check_pip():
        print()
        print_status("Установка pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
            print_success("pip установлен")
        except:
            print_error("Не удалось установить pip")
            input("\nНажмите Enter для выхода...")
            sys.exit(1)

    # Установка компонентов
    yt_ok = install_yt_dlp()
    ffmpeg_ok = install_ffmpeg()

    # Итог
    print()
    print("=" * 55)
    print("  РЕЗУЛЬТАТ")
    print("=" * 55)
    print()

    if yt_ok:
        print_success("yt-dlp — готов")
    else:
        print_error("yt-dlp — требуется установка")

    if ffmpeg_ok:
        print_success("ffmpeg — готов")
    else:
        print_warning("ffmpeg — MP3 и Full HD недоступны")

    print()

    if yt_ok:
        print("=" * 55)
        print("  ✅ ПРОГРАММА ГОТОВА К РАБОТЕ")
        print("=" * 55)
        print()
        print("  Запустите: python3 media_downloader_mac.py")
    else:
        print("=" * 55)
        print("  ⚠️  УСТРАНИТЕ ОШИБКИ И ЗАПУСТИТЕ СНОВА")
        print("=" * 55)

    print()
    input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()