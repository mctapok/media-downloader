import yt_dlp
import os
import sys
import shutil
import socket
import time
import threading
import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


# ================= ПОИСК FFMPEG (кроссплатформенный) =================
def find_ffmpeg():
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return os.path.dirname(system_ffmpeg)

    # macOS: Homebrew
    if platform.system() == "Darwin":
        brew_paths = [
            "/opt/homebrew/bin",
            "/usr/local/bin",
            "/opt/local/bin",
        ]
        for path in brew_paths:
            if os.path.exists(os.path.join(path, "ffmpeg")):
                return path

    # Локальная папка
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "bin")
    if os.path.exists(os.path.join(local_path, "ffmpeg")):
        return local_path

    return None


FFMPEG_PATH = find_ffmpeg()


# ================= ОСНОВНОЙ КЛАСС =================
class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        is_mac = platform.system() == "Darwin"
        self.root.title("Загрузчик медиа")

        # Подгоняем размер под macOS
        is_mac = platform.system() == "Darwin"
        default_font = "SF Pro Text" if is_mac else "Segoe UI"

        self.root.geometry("700x600")
        self.root.resizable(True, True)
        self.root.minsize(600, 500)

        if is_mac:
            self.accent = "#007AFF"
            self.accent_hover = "#3399FF"
            self.bg_color = "#F5F5F5"
            self.card_color = "#FFFFFF"
            self.fg_color = "#1D1D1F"
            self.warning_color = "#FF9500"
            self.success_color = "#34C759"
            entry_bg = "#E5E5EA"
            entry_fg = "#1D1D1F"
            menu_bg = "#FFFFFF"
            menu_fg = "#1D1D1F"
            radio_bg = "#FFFFFF"
            radio_fg = "#1D1D1F"
            select_color = "#FFFFFF"
        else:
            self.accent = "#e94560"
            self.accent_hover = "#ff6b81"
            self.bg_color = "#1a1a2e"
            self.card_color = "#16213e"
            self.fg_color = "#e0e0e0"
            self.warning_color = "#f39c12"
            self.success_color = "#2ecc71"
            entry_bg = "#0f3460"
            entry_fg = "#e0e0e0"
            menu_bg = "#0f3460"
            menu_fg = "#e0e0e0"
            radio_bg = "#16213e"
            radio_fg = "#e0e0e0"
            select_color = "#16213e"

        self.root.configure(bg=self.bg_color)

        # Для macOS — делаем окно поверх других
        if is_mac:
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))

        # Заголовок
        title_frame = tk.Frame(root, bg=self.bg_color)
        title_frame.pack(pady=(20, 5), fill="x")

        tk.Label(
            title_frame, text="⬇ Загрузчик медиа",
            font=(default_font, 20, "bold"),
            bg=self.bg_color, fg=self.accent
        ).pack()

        tk.Label(
            title_frame,
            text="YouTube • Rutube • VK • Twitch и сотни других сайтов",
            font=(default_font, 10),
            bg=self.bg_color, fg="#888888"
        ).pack()

        # Основной контейнер
        main_frame = tk.Frame(root, bg=self.card_color, bd=0)
        main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Секция: Ссылка
        link_section = tk.Frame(main_frame, bg=self.card_color)
        link_section.pack(pady=(15, 5), padx=20, fill="x")

        tk.Label(
            link_section, text="🔗 Ссылка на видео:",
            font=(default_font, 12, "bold"),
            bg=self.card_color, fg=self.fg_color
        ).pack(anchor="w")

        self.link_entry = tk.Entry(
            link_section,
            font=(default_font, 11),
            bg=entry_bg,
            fg=entry_fg,
            insertbackground=entry_fg,
            relief="flat",
            bd=10
        )
        self.link_entry.pack(fill="x", pady=(8, 0))
        self.link_entry.focus_set()

        # Контекстное меню
        self.context_menu = tk.Menu(self.link_entry, tearoff=0, bg=entry_bg, fg=entry_fg)
        self.context_menu.add_command(label="📋 Вставить", command=self.paste_text)
        self.context_menu.add_command(label="✂️ Вырезать", command=self.cut_text)
        self.context_menu.add_command(label="📄 Копировать", command=self.copy_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Очистить", command=self.clear_text)

        self.link_entry.bind("<Button-2>" if is_mac else "<Button-3>", self.show_context_menu)
        self.link_entry.bind("<Button-3>", self.show_context_menu)
        self.link_entry.bind("<Command-v>" if is_mac else "<Control-v>", self.paste_text)
        self.link_entry.bind("<Command-V>" if is_mac else "<Control-V>", self.paste_text)

        tk.Label(
            link_section,
            text="💡 ПКМ → Вставить  |  ⌘V" if is_mac else "💡 ПКМ → Вставить  |  Ctrl+V",
            font=(default_font, 8),
            bg=self.card_color, fg="#666666"
        ).pack(anchor="w", pady=(2, 0))

        # Секция: Формат
        format_section = tk.Frame(main_frame, bg=self.card_color)
        format_section.pack(pady=(15, 5), padx=20, fill="x")

        tk.Label(
            format_section, text="🎯 Формат:",
            font=(default_font, 12, "bold"),
            bg=self.card_color, fg=self.fg_color
        ).pack(anchor="w")

        self.format_var = tk.StringVar(value="mp4")

        radio_frame = tk.Frame(format_section, bg=self.card_color)
        radio_frame.pack(anchor="w", pady=(8, 0))

        self.mp4_radio = tk.Radiobutton(
            radio_frame,
            text="🎬 Видео (MP4) — до 1080p",
            variable=self.format_var, value="mp4",
            font=(default_font, 11),
            bg=self.card_color, fg=self.fg_color,
            selectcolor=self.card_color,
            activebackground=self.card_color,
            activeforeground=self.accent
        )
        self.mp4_radio.pack(anchor="w", pady=(0, 5))

        self.mp3_radio = tk.Radiobutton(
            radio_frame,
            text="🎵 Аудио (MP3) — 192 kbps",
            variable=self.format_var, value="mp3",
            font=(default_font, 11),
            bg=self.card_color, fg=self.fg_color,
            selectcolor=self.card_color,
            activebackground=self.card_color,
            activeforeground=self.accent
        )
        self.mp3_radio.pack(anchor="w")

        if not FFMPEG_PATH:
            tk.Label(
                format_section,
                text="⚠️ ffmpeg не найден! Установите: brew install ffmpeg",
                font=(default_font, 9),
                bg=self.card_color, fg=self.warning_color
            ).pack(anchor="w", pady=(5, 0))
            self.mp3_radio.config(state="disabled")

        # Секция: Папка
        folder_section = tk.Frame(main_frame, bg=self.card_color)
        folder_section.pack(pady=(15, 5), padx=20, fill="x")

        tk.Label(
            folder_section, text="📁 Папка для сохранения:",
            font=(default_font, 12, "bold"),
            bg=self.card_color, fg=self.fg_color
        ).pack(anchor="w")

        folder_select_frame = tk.Frame(folder_section, bg=self.card_color)
        folder_select_frame.pack(fill="x", pady=(8, 0))

        # macOS: папка Downloads по умолчанию
        default_download = os.path.join(os.path.expanduser("~"), "Downloads", "VideoDownloader")
        self.folder_path = tk.StringVar(value=default_download)

        self.folder_entry = tk.Entry(
            folder_select_frame,
            textvariable=self.folder_path,
            font=(default_font, 10),
            bg="#0f3460", fg="#888888",
            relief="flat", bd=8,
            state="readonly"
        )
        self.folder_entry.pack(side="left", fill="x", expand=True)

        tk.Button(
            folder_select_frame,
            text="📂 Обзор",
            command=self.browse_folder,
            font=(default_font, 10),
            bg="#0f3460", fg=self.fg_color,
            relief="flat", bd=8,
            cursor="hand2",
            activebackground="#1a1a4e",
            activeforeground=self.fg_color
        ).pack(side="right", padx=(8, 0))

        # Кнопка скачивания
        self.download_btn = tk.Button(
            main_frame,
            text="⬇ СКАЧАТЬ",
            command=self.start_download,
            font=(default_font, 14, "bold"),
            bg=self.accent, fg=entry_fg,
            relief="flat", bd=12,
            cursor="hand2",
            activebackground=self.accent_hover,
            activeforeground=entry_fg,
            highlightthickness=0,
            borderwidth=0
        )
        self.download_btn.pack(pady=20, ipadx=60)

        # Статус
        self.status_frame = tk.Frame(main_frame, bg=self.card_color)
        self.status_frame.pack(pady=(0, 15), padx=20, fill="x")

        self.status_label = tk.Label(
            self.status_frame,
            text="✅ Готов к загрузке",
            font=(default_font, 10),
            bg=self.card_color, fg=self.success_color
        )
        self.status_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            mode='indeterminate',
            length=200
        )

        self.download_thread = None
        self.root.bind('<Return>', lambda e: self.start_download())

    # ================= МЕТОДЫ ИНТЕРФЕЙСА =================
    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def paste_text(self, event=None):
        try:
            clipboard_text = self.root.clipboard_get()
            if clipboard_text:
                if self.link_entry.selection_present():
                    self.link_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.link_entry.insert(self.link_entry.index(tk.INSERT), clipboard_text)
        except:
            pass
        return "break"

    def copy_text(self, event=None):
        try:
            if self.link_entry.selection_present():
                self.root.clipboard_clear()
                self.root.clipboard_append(self.link_entry.selection_get())
        except:
            pass
        return "break"

    def cut_text(self, event=None):
        try:
            if self.link_entry.selection_present():
                self.root.clipboard_clear()
                self.root.clipboard_append(self.link_entry.selection_get())
                self.link_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
        return "break"

    def clear_text(self):
        self.link_entry.delete(0, tk.END)

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_path.get())
        if folder:
            self.folder_path.set(folder)

    def update_status(self, text, color=None):
        if color is None:
            color = self.warning_color
        self.root.after(0, lambda: self.status_label.config(text=text, fg=color))

    def reset_ui(self):
        self.download_btn.config(state="normal", text="⬇ СКАЧАТЬ")
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

    # ================= ОБХОД БЛОКИРОВКИ =================
    def warmup_connection(self):
        warmup_hosts = [
            ("rutube.ru", 443),
            ("vk.ru", 443),
            ("ya.ru", 443),
            ("mail.ru", 443),
        ]
        for host, port in warmup_hosts:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((host, port))
                s.close()
            except:
                pass

    # ================= ЗАГРУЗКА =================
    def start_download(self):
        url = self.link_entry.get().strip()
        if not url:
            messagebox.showwarning("Пустая ссылка", "Вставьте ссылку на видео.")
            self.link_entry.focus_set()
            return

        self.download_btn.config(state="disabled", text="⏳ ЗАГРУЗКА...")
        self.progress_bar.pack(fill="x", pady=(8, 0))
        self.progress_bar.start()
        self.status_label.config(text="🔄 Подготовка...", fg=self.warning_color)

        if "youtube.com" in url or "youtu.be" in url:
            self.warmup_connection()

        self.download_thread = threading.Thread(
            target=self.download_media,
            args=(url,),
            daemon=True
        )
        self.download_thread.start()

    def download_media(self, url):
        output_dir = self.folder_path.get()
        os.makedirs(output_dir, exist_ok=True)

        format_choice = self.format_var.get()

        if format_choice == "mp3" and FFMPEG_PATH:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
                'ffmpeg_location': FFMPEG_PATH,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'extractor_retries': 20,
                'retries': 20,
                'fragment_retries': 20,
                'retry_sleep_functions': {'http': lambda n: 3, 'fragment': lambda n: 3},
                'socket_timeout': 30,
                'force_ipv4': True,
            }
        elif FFMPEG_PATH:
            ydl_opts = {
                'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
                'ffmpeg_location': FFMPEG_PATH,
                'merge_output_format': 'mp4',
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'extractor_retries': 20,
                'retries': 20,
                'fragment_retries': 20,
                'retry_sleep_functions': {'http': lambda n: 3, 'fragment': lambda n: 3},
                'socket_timeout': 30,
                'force_ipv4': True,
            }
        else:
            ydl_opts = {
                'format': 'best[height<=720]',
                'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'extractor_retries': 20,
                'retries': 20,
                'fragment_retries': 20,
                'retry_sleep_functions': {'http': lambda n: 3, 'fragment': lambda n: 3},
                'socket_timeout': 30,
                'force_ipv4': True,
            }

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.update_status(f"🔄 Попытка {attempt}/{max_attempts}...")

                    if attempt > 1 and ("youtube.com" in url or "youtu.be" in url):
                        self.update_status("🔄 Обход блокировки...")
                        self.warmup_connection()
                        time.sleep(2)

                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Неизвестное название')

                    self.update_status(f"⬇ Загрузка: {title[:50]}...")
                    ydl.download([url])

                self.update_status("✅ Готово!", self.success_color)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно", f"✅ Видео сохранено!\n\n📁 {output_dir}"
                ))
                self.root.after(0, self.reset_ui)
                return

            except Exception as e:
                error_msg = str(e)
                is_reset = any(x in error_msg for x in [
                    "Remote end closed", "разорвал", "timeout", "timed out",
                    "Connection reset", "ConnectionResetError"
                ])

                if is_reset and attempt < max_attempts:
                    self.update_status(f"⚠️ Сбой. Повтор через 3 сек...")
                    time.sleep(3)
                    continue

                if "HTTP Error 403" in error_msg:
                    error_msg = "Доступ запрещён (403)."
                elif "HTTP Error 429" in error_msg:
                    error_msg = "Слишком много запросов."
                elif "Private video" in error_msg:
                    error_msg = "Приватное видео."
                elif is_reset:
                    error_msg = "YouTube заблокирован. Включите VPN."

                self.update_status("❌ Ошибка", self.accent)
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"❌ {error_msg}"))
                break

        self.root.after(0, self.reset_ui)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '')
            eta = d.get('_eta_str', '')
            status = f"⬇ {percent}"
            if speed:
                status += f" | {speed}"
            if eta:
                status += f" | Осталось: {eta}"
            self.update_status(status)
        elif d['status'] == 'finished':
            self.update_status("🔄 Обработка...")


# ================= ЗАПУСК =================
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()
