import yt_dlp
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Путь к ffmpeg
FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-2026-06-15-git-44d082edc8-full_build\bin"


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Загрузчик видео / аудио")
        self.root.geometry("650x500")
        self.root.resizable(True, True)
        self.root.minsize(550, 450)

        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent = "#ff4757"
        self.root.configure(bg=self.bg_color)

        # Заголовок
        title = tk.Label(
            root, text="⬇ Загрузчик медиа",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_color, fg=self.accent
        )
        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            root, text="YouTube, Rutube, VK и сотни других сайтов",
            font=("Segoe UI", 10),
            bg=self.bg_color, fg="#888888"
        )
        subtitle.pack(pady=(0, 20))

        # Фрейм для ссылки
        link_frame = tk.Frame(root, bg=self.bg_color)
        link_frame.pack(pady=5, padx=30, fill="x")

        tk.Label(
            link_frame, text="Ссылка на видео:",
            font=("Segoe UI", 11),
            bg=self.bg_color, fg=self.fg_color
        ).pack(anchor="w")

        # ПОЛЕ ВВОДА ССЫЛКИ с обработкой ПКМ
        self.link_entry = tk.Entry(
            link_frame,
            font=("Segoe UI", 11),
            bg="#2d2d2d",
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief="flat",
            bd=8
        )
        self.link_entry.pack(fill="x", pady=(5, 0))
        self.link_entry.focus_set()

        # Создаём контекстное меню для поля ввода
        self.context_menu = tk.Menu(self.link_entry, tearoff=0, bg="#2d2d2d", fg=self.fg_color)
        self.context_menu.add_command(label="Вставить", command=self.paste_text)
        self.context_menu.add_command(label="Вырезать", command=self.cut_text)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Очистить", command=self.clear_text)

        # Привязываем ПКМ к показу меню
        self.link_entry.bind("<Button-3>", self.show_context_menu)

        # Привязываем Ctrl+V вручную
        self.link_entry.bind("<Control-v>", self.paste_text)
        self.link_entry.bind("<Control-V>", self.paste_text)
        self.link_entry.bind("<Control-c>", self.copy_text)
        self.link_entry.bind("<Control-C>", self.copy_text)
        self.link_entry.bind("<Control-x>", self.cut_text)
        self.link_entry.bind("<Control-X>", self.cut_text)
        self.link_entry.bind("<Control-a>", self.select_all)
        self.link_entry.bind("<Control-A>", self.select_all)

        # Подсказка
        hint_label = tk.Label(
            link_frame,
            text="ПКМ по полю → Вставить | Ctrl+V | Перетащите текст",
            font=("Segoe UI", 8),
            bg=self.bg_color, fg="#666666"
        )
        hint_label.pack(anchor="w", pady=(2, 0))

        # Фрейм для выбора формата
        format_frame = tk.Frame(root, bg=self.bg_color)
        format_frame.pack(pady=15, padx=30, fill="x")

        tk.Label(
            format_frame, text="Формат:",
            font=("Segoe UI", 11),
            bg=self.bg_color, fg=self.fg_color
        ).pack(anchor="w")

        self.format_var = tk.StringVar(value="mp4")

        radio_frame = tk.Frame(format_frame, bg=self.bg_color)
        radio_frame.pack(anchor="w", pady=(5, 0))

        self.mp4_radio = tk.Radiobutton(
            radio_frame, text="🎬 Видео (MP4) — до 1080p",
            variable=self.format_var, value="mp4",
            font=("Segoe UI", 11),
            bg=self.bg_color, fg=self.fg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.accent
        )
        self.mp4_radio.pack(anchor="w")

        self.mp3_radio = tk.Radiobutton(
            radio_frame, text="🎵 Аудио (MP3) — 192 kbps",
            variable=self.format_var, value="mp3",
            font=("Segoe UI", 11),
            bg=self.bg_color, fg=self.fg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.accent
        )
        self.mp3_radio.pack(anchor="w")

        # Фрейм для выбора папки
        folder_frame = tk.Frame(root, bg=self.bg_color)
        folder_frame.pack(pady=5, padx=30, fill="x")

        tk.Label(
            folder_frame, text="Папка для сохранения:",
            font=("Segoe UI", 11),
            bg=self.bg_color, fg=self.fg_color
        ).pack(anchor="w")

        folder_select_frame = tk.Frame(folder_frame, bg=self.bg_color)
        folder_select_frame.pack(fill="x", pady=(5, 0))

        self.folder_path = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))

        self.folder_entry = tk.Entry(
            folder_select_frame,
            textvariable=self.folder_path,
            font=("Segoe UI", 10),
            bg="#2d2d2d", fg="#888888",
            relief="flat", bd=8,
            state="readonly"
        )
        self.folder_entry.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Button(
            folder_select_frame,
            text="📁 Выбрать",
            command=self.browse_folder,
            font=("Segoe UI", 10),
            bg="#3d3d3d", fg=self.fg_color,
            relief="flat", bd=6,
            cursor="hand2",
            activebackground="#4d4d4d",
            activeforeground=self.fg_color
        )
        browse_btn.pack(side="right", padx=(5, 0))

        # Кнопка загрузки
        self.download_btn = tk.Button(
            root,
            text="⬇ СКАЧАТЬ",
            command=self.start_download,
            font=("Segoe UI", 13, "bold"),
            bg=self.accent, fg="#ffffff",
            relief="flat", bd=10,
            cursor="hand2",
            activebackground="#ff6b81",
            activeforeground="#ffffff"
        )
        self.download_btn.pack(pady=20, ipadx=40)

        # Прогресс
        self.progress_frame = tk.Frame(root, bg=self.bg_color)
        self.progress_frame.pack(pady=5, padx=30, fill="x")

        self.status_label = tk.Label(
            self.progress_frame,
            text="Готов к загрузке",
            font=("Segoe UI", 10),
            bg=self.bg_color, fg="#aaaaaa"
        )
        self.status_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='indeterminate',
            length=200
        )

        self.download_thread = None

    def show_context_menu(self, event):
        """Показать контекстное меню по правому клику"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def paste_text(self, event=None):
        """Вставить текст из буфера обмена"""
        try:
            clipboard_text = self.root.clipboard_get()
            if clipboard_text:
                # Если есть выделенный текст — заменяем его
                if self.link_entry.selection_present():
                    self.link_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
                # Вставляем в позицию курсора
                cursor_pos = self.link_entry.index(tk.INSERT)
                self.link_entry.insert(cursor_pos, clipboard_text)
        except:
            pass
        return "break"  # Предотвращаем стандартную обработку

    def copy_text(self, event=None):
        """Копировать выделенный текст"""
        try:
            if self.link_entry.selection_present():
                selected_text = self.link_entry.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
        except:
            pass
        return "break"

    def cut_text(self, event=None):
        """Вырезать выделенный текст"""
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
        """Очистить поле ввода"""
        self.link_entry.delete(0, tk.END)

    def select_all(self, event=None):
        """Выделить весь текст"""
        self.link_entry.select_range(0, tk.END)
        self.link_entry.icursor(tk.END)
        return "break"

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

        self.download_btn.config(state="disabled", text="ЗАГРУЗКА...")
        self.progress_bar.pack(fill="x", pady=(5, 0))
        self.progress_bar.start()
        self.status_label.config(text="Подготовка...")

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

        if format_choice == "mp3":
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
                'quiet': False,
                'extractor_retries': 5,
                'fragment_retries': 5,
                'retries': 5,
                'socket_timeout': 30,
                'force_ipv4': True,
            }
        else:
            ydl_opts = {
                'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
                'ffmpeg_location': FFMPEG_PATH,
                'merge_output_format': 'mp4',
                'progress_hooks': [self.progress_hook],
                'quiet': False,
                'extractor_retries': 5,
                'fragment_retries': 5,
                'retries': 5,
                'socket_timeout': 30,
                'force_ipv4': True,
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.update_status("Получение информации о видео...")
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Неизвестное название')

                self.update_status(f"Загрузка: {title[:60]}...")
                ydl.download([url])

            self.show_success(f"✅ Готово!\nФайл сохранён в:\n{output_dir}")

        except Exception as e:
            error_msg = str(e)
            if "HTTP Error 403" in error_msg:
                error_msg = "Ошибка доступа (403). Возможно, видео заблокировано или недоступно."
            elif "Private video" in error_msg:
                error_msg = "Это приватное видео. Доступ к нему ограничен."
            elif "Remote end closed" in error_msg or "разорвал" in error_msg:
                error_msg = (
                    "Сервер разорвал соединение.\n\n"
                    "Возможные причины:\n"
                    "• YouTube заблокирован (включите VPN)\n"
                    "• Попробуйте ещё раз\n"
                    "• Обновите yt-dlp: pip install -U yt-dlp"
                )
            self.show_error(f"❌ Ошибка загрузки:\n{error_msg}")

        finally:
            self.reset_ui()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '')
            eta = d.get('_eta_str', '')
            status = f"Загрузка: {percent}"
            if speed:
                status += f" | Скорость: {speed}"
            if eta:
                status += f" | Осталось: {eta}"
            self.update_status(status)
        elif d['status'] == 'finished':
            self.update_status("Обработка файла...")

    def update_status(self, text):
        self.root.after(0, lambda: self.status_label.config(text=text))

    def show_success(self, text):
        self.root.after(0, lambda: messagebox.showinfo("Успешно", text))

    def show_error(self, text):
        self.root.after(0, lambda: messagebox.showerror("Ошибка", text))

    def reset_ui(self):
        self.root.after(0, self._reset_ui)

    def _reset_ui(self):
        self.download_btn.config(state="normal", text="⬇ СКАЧАТЬ")
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.status_label.config(text="Готов к загрузке")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()