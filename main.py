from tkinter import filedialog, messagebox, StringVar
import customtkinter as ctk
import threading
import yt_dlp
import os

class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("YouTube Video Downloader")
        self.geometry("650x550")
        self.resizable(False, False)
        self.center_window()
        self.create_widgets()

    def create_widgets(self):
        self.url_frame = ctk.CTkFrame(self, corner_radius=10)
        self.url_frame.pack(pady=25, padx=20, fill="x", expand=False)
        self.url_entry = ctk.CTkEntry(self.url_frame, width=400, placeholder_text="Enter YouTube video URL", font=("Cascadia Mono", 14))
        self.url_entry.pack(side="left", padx=(7, 20), pady=5, fill="x", expand=True)
        self.send_url_button = ctk.CTkButton(self.url_frame, text="Send", command=self.load_resolutions, height=45, width=90, font=("Cascadia Mono", 14))
        self.send_url_button.pack(side="right")

        self.resolution_var = StringVar(value="Select Resolution")
        self.resolution_menu = ctk.CTkOptionMenu(self, variable=self.resolution_var, values=[], height=45, width=230, font=("Cascadia Mono", 14))
        self.resolution_menu.pack(pady=10)
        self.resolution_menu.configure(state="disabled")

        self.directory_button = ctk.CTkButton(self, text="Select Download Directory", command=self.select_directory, height=45, width=230, font=("Cascadia Mono", 14))
        self.directory_button.pack(pady=10)
        self.directory_button.configure(state="disabled")
        self.directory_label_frame = ctk.CTkFrame(self, corner_radius=10)
        self.directory_label_frame.pack(pady=(12, 5))
        self.directory_label = ctk.CTkLabel(self.directory_label_frame, text="No directory selected", font=("Cascadia Mono", 15), wraplength=550)
        self.directory_label.pack(pady=5, padx=10)
        
        self.progress_frame = ctk.CTkFrame(self, corner_radius=25, width=500, height=35)
        self.progress_frame.pack(pady=20)
        self.progress = ctk.CTkProgressBar(self.progress_frame, width=480, height=25, bg_color="#2e2e2e")
        self.progress.pack(pady=7, padx=7)
        self.progress.set(0)

        self.info_frame = ctk.CTkFrame(self, corner_radius=15)
        self.info_frame.pack(pady=0, padx=20)
        self.estimate_label = ctk.CTkLabel(self.info_frame, text="Estimated Time: N/A", font=("Cascadia Mono", 14), bg_color="#2e2e2e")
        self.estimate_label.pack(pady=(5, 1), padx=10)
        self.progress_label = ctk.CTkLabel(self.info_frame, text="Progress: 0% (0 MB/s)", font=("Cascadia Mono", 14), bg_color="#2e2e2e")
        self.progress_label.pack(pady=1, padx=10)
        self.size_label = ctk.CTkLabel(self.info_frame, text="Size: N/A", font=("Cascadia Mono", 14), bg_color="#2e2e2e")
        self.size_label.pack(pady=(1, 5), padx=10)
        
        self.download_button = ctk.CTkButton(self, text="Download Video", command=self.start_download, height=45, width=230, font=("Cascadia Mono", 14))
        self.download_button.pack(pady=20)
        self.download_button.configure(state="disabled")

        self.download_directory = ""
        self.last_downloaded_bytes = 0
        self.last_update_time = None

    def center_window(self):
        self.geometry(f'{650}x{550}+{int((self.winfo_screenwidth() / 2) - (650 / 2))}+{int((self.winfo_screenheight() / 2) - (550 / 2))}')

    def select_directory(self):
        self.download_directory = filedialog.askdirectory()
        if self.download_directory:
            self.directory_label.configure(text=self.download_directory)
            self.download_button.configure(state="normal")

    def start_download(self):
        threading.Thread(target=self.download_video).start()

    def download_video(self):
        url = self.url_entry.get()
        if not url:
            self.after(0, lambda: messagebox.showerror("Error", "Please enter a video URL"))
            return
        if not self.download_directory:
            self.after(0, lambda: messagebox.showerror("Error", "Please select a download directory"))
            return
        
        selected_resolution = self.resolution_var.get()
        if selected_resolution and selected_resolution != "Select Resolution":
            format_selector = f"bestvideo[height<={selected_resolution.replace('p', '')}]+bestaudio/best"
        else:
            format_selector = "best"

        ydl_opts = {
            'format': format_selector,
            'outtmpl': os.path.join(self.download_directory, '%(title)s (%(height)sp).%(ext)s'),
            'progress_hooks': [self.update_progress]
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, self.download_complete)
        except Exception as e:
            if "ffmpeg" in str(e):
                self.after(0, lambda: messagebox.showerror("Error: FFmpeg is not installed", f"FFmpeg is not installed or not installed properly. Please check the FFmpeg installation and try again."))
            else:
                self.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred. If the error persists, report it to the developer."))

    def update_progress(self, d):
        if d['status'] == 'downloading':
            downloaded_bytes = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes', 1)
            percent = (downloaded_bytes / total_bytes) * 100

            if downloaded_bytes > 0 and self.last_update_time is not None:
                elapsed_time = d.get('elapsed', 0)
                download_speed = (downloaded_bytes - self.last_downloaded_bytes) / (elapsed_time - self.last_update_time + 0.001)
                remaining_bytes = total_bytes - downloaded_bytes
                estimated_time = remaining_bytes / download_speed
                minutes, seconds = divmod(int(estimated_time), 60)
                download_speed_mb_s = download_speed / (1024 * 1024)

                self.estimate_label.configure(text=f"Estimated Time: {minutes}m {seconds}s")
                self.progress_label.configure(text=f"Progress: {int(percent)}% ({download_speed_mb_s:.2f} MB/s)")
            else:
                self.estimate_label.configure(text="Estimated Time: Calculating...")
                self.progress_label.configure(text="Progress: 0% (0 MB/s)")

            self.after(0, lambda: self.progress.set(percent / 100))

            total_size_mb = total_bytes / (1024 * 1024)
            self.size_label.configure(text=f"Size: {total_size_mb:.2f} MB / {(downloaded_bytes / (1024 * 1024)):.2f} MB")
            self.last_downloaded_bytes = downloaded_bytes
            self.last_update_time = d.get('elapsed', 0)

    def download_complete(self):
        self.progress.set(0)
        self.estimate_label.configure(text="Estimated Time: N/A")
        self.progress_label.configure(text="Progress: 0% (0 MB/s)")
        self.size_label.configure(text="Size: N/A")
        self.last_downloaded_bytes = 0
        self.last_update_time = None
        messagebox.showinfo("Success", "Download complete!")

    def load_resolutions(self):
        url = self.url_entry.get().strip()
        if not url:
            self.update_resolution_menu([])
            return

        valid_resolutions = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
        ydl_opts = {
            'quiet': True,
            'dumpjson': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=False)
                formats = info_dict.get('formats', [])
                available_resolutions = set()
                for fmt in formats:
                    res = fmt.get('height')
                    if res:
                        res_str = f"{res}p"
                        if res_str in valid_resolutions:
                            available_resolutions.add(res_str)
                self.update_resolution_menu(sorted(available_resolutions, key=lambda x: int(x.replace('p', ''))))
                self.resolution_menu.configure(state="normal")
                self.directory_button.configure(state="normal")
            except Exception:
                self.update_resolution_menu([])
                messagebox.showerror("Error: Failed to fetch URL data", f"'{url}' is not a valid URL.")

    def update_resolution_menu(self, resolutions):
        self.resolution_menu.configure(values=resolutions)
        if resolutions:
            self.resolution_var.set(resolutions[0])
        else:
            self.resolution_var.set("Select Resolution")

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()