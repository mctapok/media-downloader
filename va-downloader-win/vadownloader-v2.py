import yt_dlp
import os
import sys
import shutil
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


# Поиск ffmpeg
def find_ffmpeg():
    # Проверяем системный ffmpeg
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return os.path.dirname(system_ffmpeg)

    # Проверяем локальный ffmpeg
    local_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "bin"),
        os.path.join(os.getcwd(), "ffmpeg", "bin"),
        r"C:\ffmpeg\bin",
    ]
    for path in local_paths:
        if os.path.exists(os.path.join(path, "ffmpeg.exe")):
            return path

    return None


FFMPEG_PATH = find_ffmpeg()


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Загрузчик видео / аудио")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        self.root.minsize(600, 500)

        self.bg_color = "#1a1a2e"
        self.card_color = "#16213e"
        self.fg_color = "#e0e0e0"
        self.accent = "#e94560"
        self.accent_hover = "#ff6b81"
        self.success_color = "#2ecc71"
        self.warning_color = "#f39c12"

        self.root.configure(bg=self.bg_color)

        # Заголовок
        title_frame = tk.Frame(root, bg=self.bg_color)
        title_frame.pack(pady=(20, 5), fill="x")

        title = tk.Label(
            title_frame, text="⬇ Загрузчик медиа",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_color, fg=self.accent
        )
        title.pack()

        subtitle = tk.Label(
            title_frame,
            text="YouTube • Rutube • VK • Twitch и сотни других сайтов \n из-за работы DPI в РФ могут возникнуть ошибки 403 и сброс соединения,\nпопробуйте явно скачать видео с rutube и др. так же попробуйте повторно нажать скачать",
            font=("Segoe UI", 10),
            bg=self.bg_color, fg="#888888"
        )
        subtitle.pack()

        # Основной контейнер
        main_frame = tk.Frame(root, bg=self.card_color, bd=0, highlightthickness=0)
        main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Секция: Ссылка
        link_section = tk.Frame(main_frame, bg=self.card_color)
        link_section.pack(pady=(15, 5), padx=20, fill="x")

        tk.Label(
            link_section, text="🔗 Ссылка на видео:",
            font=("Segoe UI", 12, "bold"),
            bg=self.card_color, fg=self.fg_color
        ).pack(anchor="w")

        self.link_entry = tk.Entry(
            link_section,
            font=("Segoe UI", 11),
            bg="#0f3460",
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief="flat",
            bd=10
        )
        self.link_entry.pack(fill="x", pady=(8, 0))
        self.link_entry.focus_set()

        # Контекстное меню
        self.context_menu = tk.Menu(self.link_entry, tearoff=0, bg="#0f3460", fg=self.fg_color)
        self.context_menu.add_command(label="📋 Вставить", command=self.paste_text)
        self.context_menu.add_command(label="✂️ Вырезать", command=self.cut_text)
        self.context_menu.add_command(label="📄 Копировать", command=self.copy_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Очистить", command=self.clear_text)

        self.link_entry.bind("<Button-3>", self.show_context_menu)
        self.link_entry.bind("<Control-v>", self.paste_text)
        self.link_entry.bind("<Control-V>", self.paste_text)

        hint = tk.Label(
            link_section,
            text="💡 ПКМ → Вставить  |  Ctrl+V",
            font=("Segoe UI", 8),
            bg=self.card_color, fg="#666666"
        )
        hint.pack(anchor="w", pady=(2, 0))

        # Секция: Формат
        format_section = tk.Frame(main_frame, bg=self.card_color)
        format_section.pack(pady=(15, 5), padx=20, fill="x")

        tk.Label(
            format_section, text="🎯 Формат:",
            font=("Segoe UI", 12, "bold"),
            bg=self.card_color, fg=self.fg_color
        ).pack(anchor="w")

        self.format_var = tk.StringVar(value="mp4")

        radio_frame = tk.Frame(format_section, bg=self.card_color)
        radio_frame.pack(anchor="w", pady=(8, 0))

        self.mp4_radio = tk.Radiobutton(
            radio_frame,
            text="🎬 Видео (MP4) — до 1080p",
            variable=self.format_var, value="mp4",
            font=("Segoe UI", 11),
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
            font=("Segoe UI", 11),
            bg=self.card_color, fg=self.fg_color,
            selectcolor=self.card_color,
            activebackground=self.card_color,
            activeforeground=self.accent
        )
        self.mp3_radio.pack(anchor="w")

        # Предупреждение, если нет ffmpeg
        if not FFMPEG_PATH:
            self.ffmpeg_warning = tk.Label(
                format_section,
                text="⚠️ ffmpeg не найден! MP3 и Full HD недоступны.",
                font=("Segoe UI", 9),
                bg=self.card_color, fg=self.warning_color
            )
            self.ffmpeg_warning.pack(anchor="w", pady=(5, 0))
            self.mp3_radio.config(state="disabled")

        # Секция: Папка
        folder_section = tk.Frame(main_frame, bg=self.card_color)
        folder_section.pack(pady=(15, 5), padx=20, fill="x")

        tk.Label(
            folder_section, text="📁 Папка для сохранения:",
            font=("Segoe UI", 12, "bold"),
            bg=self.card_color, fg=self.fg_color
        ).pack(anchor="w")

        folder_select_frame = tk.Frame(folder_section, bg=self.card_color)
        folder_select_frame.pack(fill="x", pady=(8, 0))

        self.folder_path = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))

        self.folder_entry = tk.Entry(
            folder_select_frame,
            textvariable=self.folder_path,
            font=("Segoe UI", 10),
            bg="#0f3460", fg="#888888",
            relief="flat", bd=8,
            state="readonly"
        )
        self.folder_entry.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Button(
            folder_select_frame,
            text="📂 Обзор",
            command=self.browse_folder,
            font=("Segoe UI", 10),
            bg="#0f3460", fg=self.fg_color,
            relief="flat", bd=8,
            cursor="hand2",
            activebackground="#1a1a4e",
            activeforeground=self.fg_color
        )
        browse_btn.pack(side="right", padx=(8, 0))

        # Кнопка скачивания
        self.download_btn = tk.Button(
            main_frame,
            text="⬇ СКАЧАТЬ",
            command=self.start_download,
            font=("Segoe UI", 14, "bold"),
            bg=self.accent, fg="#ffffff",
            relief="flat", bd=12,
            cursor="hand2",
            activebackground=self.accent_hover,
            activeforeground="#ffffff"
        )
        self.download_btn.pack(pady=20, ipadx=60)

        # Статус
        self.status_frame = tk.Frame(main_frame, bg=self.card_color)
        self.status_frame.pack(pady=(0, 15), padx=20, fill="x")

        self.status_label = tk.Label(
            self.status_frame,
            text="✅ Готов к загрузке",
            font=("Segoe UI", 10),
            bg=self.card_color, fg=self.success_color
        )
        self.status_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            mode='indeterminate',
            length=200
        )

        self.download_thread = None

        # Привязка горячих клавиш
        self.root.bind('<Return>', lambda e: self.start_download())

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
                cursor_pos = self.link_entry.index(tk.INSERT)
                self.link_entry.insert(cursor_pos, clipboard_text)
        except:
            pass
        return "break"

    def copy_text(self, event=None):
        try:
            if self.link_entry.selection_present():
                selected_text = self.link_entry.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
        except:
            pass
        return "break"

    def cut_text(self, event=None):
        try:
            if self.link_entry.selection_present():
                selected_text = self.link_entry.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
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

    def start_download(self):
        url = self.link_entry.get().strip()
        if not url:
            messagebox.showwarning("Пустая ссылка", "Пожалуйста, вставьте ссылку на видео.")
            self.link_entry.focus_set()
            return

        self.download_btn.config(state="disabled", text="⏳ ЗАГРУЗКА...")
        self.progress_bar.pack(fill="x", pady=(8, 0))
        self.progress_bar.start()
        self.status_label.config(text="🔄 Подготовка...", fg=self.warning_color)

        # ПРОГРЕВ ДЛЯ YOUTUBE
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
                # Упорные ретраи
                'extractor_retries': 20,  # Ретраи получения метаданных
                'retries': 20,  # Ретраи скачивания
                'fragment_retries': 20,  # Ретраи фрагментов (важно для DPI!)
                'retry_sleep_functions': {
                    'http': lambda n: 3,  # Ждать 3 сек между ретраями
                    'fragment': lambda n: 3,
                },
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
                # Упорные ретраи
                'extractor_retries': 20,  # Ретраи получения метаданных
                'retries': 20,  # Ретраи скачивания
                'fragment_retries': 20,  # Ретраи фрагментов (важно для DPI!)
                'retry_sleep_functions': {
                    'http': lambda n: 3,  # Ждать 3 сек между ретраями
                    'fragment': lambda n: 3,
                },
                'socket_timeout': 30,
                'force_ipv4': True,
            }
        else:
            # Без ffmpeg — только готовые файлы до 720p
            ydl_opts = {
                'format': 'best[height<=720]',
                'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                # Упорные ретраи
                'extractor_retries': 20,  # Ретраи получения метаданных
                'retries': 20,  # Ретраи скачивания
                'fragment_retries': 20,  # Ретраи фрагментов (важно для DPI!)
                'retry_sleep_functions': {
                    'http': lambda n: 3,  # Ждать 3 сек между ретраями
                    'fragment': lambda n: 3,
                },
                'socket_timeout': 30,
                'force_ipv4': True,
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.update_status("🔄 Подключение к серверу...", self.warning_color)
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Неизвестное название')

                self.update_status(f"⬇ Загрузка: {title[:50]}...", self.warning_color)
                ydl.download([url])

            self.update_status("✅ Готово!", self.success_color)
            self.root.after(0, lambda: messagebox.showinfo(
                "Успешно",
                f"✅ Видео сохранено!\n\n📁 Папка:\n{output_dir}"
            ))

        except Exception as e:
            error_msg = str(e)
            if "HTTP Error 403" in error_msg:
                error_msg = "Доступ запрещён (403). Видео может быть приватным или заблокированным."
            elif "HTTP Error 429" in error_msg:
                error_msg = "Слишком много запросов. Попробуйте через минуту."
            elif "Private video" in error_msg:
                error_msg = "Это приватное видео. Доступ ограничен."
            elif any(x in error_msg for x in ["Remote end closed", "разорвал", "timeout", "timed out"]):
                error_msg = (
                    "Не удалось подключиться к серверу.\n\n"
                    "Возможные причины:\n"
                    "• Сайт заблокирован (YouTube — нужен VPN)\n"
                    "• Проблемы с интернетом\n"
                    "• Попробуйте другой видеохостинг (Rutube/VK)"
                )
            elif "ffmpeg" in error_msg.lower():
                error_msg = "Ошибка ffmpeg. Запустите install_dependencies.py для установки."

            self.update_status("❌ Ошибка", self.accent)
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"❌ {error_msg}"))

        finally:
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
            self.update_status(status, self.warning_color)
        elif d['status'] == 'finished':
            self.update_status("🔄 Обработка файла...", self.warning_color)

    def update_status(self, text, color=None):
        if color is None:
            color = self.warning_color
        self.root.after(0, lambda: self.status_label.config(text=text, fg=color))

    def reset_ui(self):
        self.download_btn.config(state="normal", text="⬇ СКАЧАТЬ")
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

    def warmup_connection(self):
        """Прогрев соединения для обхода DPI"""
        import socket
        try:
            # Быстрое подключение к Rutube или VK
            socket.create_connection(("rutube.ru", 443), timeout=3)
            socket.create_connection(("vk.ru", 443), timeout=3)
            self.update_status("🔄 Обход блокировки...", self.warning_color)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()