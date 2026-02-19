import yt_dlp
import customtkinter
import threading
import requests
from PIL import Image
from io import BytesIO
import os
import tkinter

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.task_count = 0
        self.active_tasks = set()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }
        self.download_path = os.path.join(os.path.expanduser("~"), "Desktop", "YouTube_Downloads")
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

        self.title("download youtube video")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        #self.grid_columnconfigure(1, weight=1)

        self.input_frame = customtkinter.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=20)


        self.info_label = customtkinter.CTkLabel(self, text="", text_color="red", font=("Arial", 14))
        self.info_label.grid(row=0, column=0, pady=(100, 0))

        self.entry = customtkinter.CTkEntry(self.input_frame, placeholder_text="請輸入影片網址...", width=400)
        self.entry.pack(side="left", padx=10, pady=10)
        self.entry.bind('<Return>', lambda evnet: self.check_button_event())
        self.context_menu = tkinter.Menu(self, tearoff=0, font=("Microsoft JhengHei", 16))
        self.context_menu.add_command(label="貼上        Ctrl+V", command=self.paste_text)
        self.context_menu.add_command(label="清除", command=lambda: self.entry.delete(0, 'end'))
        self.entry.bind('<Button-3>', self.show_rightClick_Menu)
        #self.entry.grid(row=0, column=0, padx=(20,5), pady=20, sticky="e")
        self.button = customtkinter.CTkButton(self.input_frame, text="確認", command=self.check_button_event)
        #self.button.grid(row=0, column=1, padx=(5, 20), pady=20, sticky="w")
        self.button.pack(side="left", padx=10, pady=10)

        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="下載列表")
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def paste_text(self):
        try:
            text = self.clipboard_get()
            self.entry.insert('end', text)
        except:
            pass
    
    def show_rightClick_Menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def check_button_event(self):
        url = self.entry.get()
        if not url:
            print("no link input!")
            return
        
        if url in self.active_tasks:
            self.info_label.configure(text="這支影片正在下載清單中，請勿重複點擊！")
            self.after(3000, lambda: self.info_label.configure(text=""))
            return

        self.active_tasks.add(url)
        dl_task_frame = customtkinter.CTkFrame(self.scrollable_frame, fg_color="transparent")
        dl_task_frame.grid(row=self.task_count, column=0, padx=10, pady=10, sticky="ew")
        dl_task_frame.grid_columnconfigure(1, weight=1)

        pict_label = customtkinter.CTkLabel(dl_task_frame, text="loading...", width=160, height=90, fg_color="gray20", corner_radius=6)
        pict_label.grid(row=0, column=0, rowspan=2, padx=(0, 20), pady=5)

        title_label = customtkinter.CTkLabel(dl_task_frame, text=f"解析中：{url[:20]}...", anchor="w", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w")

        res_selection_str = customtkinter.StringVar(value="wating...")
        res_selection = customtkinter.CTkComboBox (
            dl_task_frame,
            values=[],
            variable=res_selection_str,
            width=150,
            state='disabled'
        )
        res_selection.grid(row=0, column=2, padx=5, sticky="e")

        status_label = customtkinter.CTkLabel(dl_task_frame, text="等待下載...", anchor="w", text_color="#0000cd", font=("Arial", 14))
        status_label.grid(row=1, column=1, sticky="w")
        
        download_button = customtkinter.CTkButton(dl_task_frame, text="下載", state="disabled", command=None, width=150)
        download_button.grid(row=1, column=2, sticky="e")

        progress_bar = customtkinter.CTkProgressBar(dl_task_frame)
        progress_bar.grid(row=2, column=0, columnspan=3, padx=0, pady=10, sticky="ew")
        progress_bar.set(0)

        task_pack = (progress_bar, status_label, title_label, pict_label, res_selection, download_button)
        thread = threading.Thread(target=self.analyze_thread, args=(url, task_pack))     
        thread.daemon = True
        thread.start()
        
        self.task_count += 1
        self.entry.delete(0, "end")

    def analyze_thread(self, video_url, ui_components):
        (p_bar, p_lbl, t_lbl, img_lbl, res_combo, dl_btn) = ui_components

        try:
            self.after(0, lambda: p_lbl.configure(text="正在獲取影片資訊...", text_color="#0000cd"))

            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(video_url, download=False)
                video_title = info.get('title', 'Unknown Tittle')
                self.after(0, lambda: t_lbl.configure(text=f"{video_title[:20]}..."))

                check_filename = f"{video_title}.mp4"
                file_path = os.path.join(self.download_path, check_filename)
                if os.path.exists(file_path):
                    self.after(0, lambda: p_lbl.configure(text="提示：此影片已經下載過啦！", text_color="red"))
                    self.after(0, lambda: dl_btn.configure(text="None", state="disabled", fg_color="gray"))

                    self.get_thumbnail(info.get('thumbnail'), img_lbl)
                    self.active_tasks.remove(video_url)
                    return
                
                # file not exist, so download it.

                self.get_thumbnail(info.get('thumbnail'), img_lbl)

                formats = info.get('formats', [])
                allowed_res = set()

                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('height') and f.get('width'):
                        h = f.get('height')
                        w = f.get('width')
                        
                        fps = f.get('fps')
                        fps = int(fps) if fps else 30

                        long_edge = max(w, h)

                        # 根據長邊解析度歸類到 YouTube 標準畫質
                        if long_edge >= 3800: std_h = 2160
                        elif long_edge >= 2500: std_h = 1440
                        elif long_edge >= 1900: std_h = 1080
                        elif long_edge >= 1200: std_h = 720
                        elif long_edge >= 800: std_h = 480
                        elif long_edge >= 600: std_h = 360
                        elif long_edge >= 400: std_h = 240
                        else: std_h = 144

                        allowed_res.add((std_h, fps))
                
                sorted_res = sorted(list(allowed_res), key=lambda x: (x[0], x[1]), reverse=True)
                
                res_options = []
                for std_h, fps in sorted_res:
                    if fps > 30:
                        res_options.append(f"{std_h}p{fps}")
                    else:
                        res_options.append(f"{std_h}p")
                res_options.append("Audio Only")

                def update_ui_ready():
                    res_combo.configure(values=res_options, state="normal")
                    if res_options:
                        res_combo.set(res_options[0])
                    p_lbl.configure(text="解析完成，請選擇畫質", text_color="green")
                    dl_btn.configure(text="下載", state="normal")
                    dl_btn.configure(command=lambda: self.start_download(video_url, ui_components))
            
            self.after(0, update_ui_ready)
        
        except Exception as e:
            print(f"解析錯誤：{e}")
            self.after(0, lambda: p_lbl.configure(text="解析失敗，請檢查連結", text_color="red"))
            self.after(0, lambda: dl_btn.configure(text="錯誤", state="disabled"))
            if video_url in self.active_tasks:
                self.active_tasks.remove(video_url)


    def get_thumbnail(self, pict_url, img_lbl):
        if not pict_url:
            return
        try:
            response = requests.get(pict_url, stream=True, headers=self.headers)
            img_data = Image.open(BytesIO(response.content))
            ctk_img = customtkinter.CTkImage(light_image=img_data, dark_image=img_data, size=(160, 90))
            self.after(0, lambda: img_lbl.configure(image=ctk_img, text=""))
        except Exception as e:
            print(f"縮圖載入失敗: {e}")

    def start_download(self, video_url, ui_components):
        (p_bar, p_lbl, t_lbl, img_lbl, res_combo, dl_btn) = ui_components
        selected_res = res_combo.get()

        if not selected_res:
            return
        
        dl_btn.configure(state="disabled", text="下載中...")
        res_combo.configure(state="disabled")

        def run_download():
            try:
                ydl_opts = {
                    'noplaylist': True,
                    'progress_hooks': [lambda d: self.update_progress(d, p_bar, p_lbl)],
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'nocolor': True,
                    'sleep_interval': 3, 
                    'max_sleep_interval': 5,
                    'user_agent': self.headers['User-Agent'],
                    'js_runtime': 'deno',
                    'remote_components': ['ejs:github'],
                }

                if selected_res == "Audio Only":
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',   
                        'preferredquality': '192',
                    }]
                else:
                    height = selected_res.split('p')[0]
                    ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
                    ydl_opts['merge_output_format'] = 'mp4'

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

                self.after(0, lambda: dl_btn.configure(text="完成", fg_color="green"))
                self.after(0, lambda: p_lbl.configure(text="下載成功！", text_color="green"))
            except Exception as e:
                self.after(0, lambda: p_lbl.configure(text=f"錯誤: {str(e)}", text_color="red"))
                self.after(0, lambda: dl_btn.configure(state="normal", text="重試"))
            finally:
                if video_url in self.active_tasks:
                    self.active_tasks.remove(video_url)

        threading.Thread(target=run_download, daemon=True).start()
        
    def update_progress(self, d, p_bar, p_lbl):
        if d['status'] == 'downloading':
            try:
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                if total > 0:
                    p_float = downloaded / total
                    p_percent = p_float * 100
                    self.after(0, lambda: p_bar.set(p_float))
                    self.after(0, lambda: p_lbl.configure(text=f"下載中: {p_percent:.1f}%"))
                else:
                    self.after(0, lambda: p_lbl.configure(text="下載中... (大小未知)"))
            except Exception:
                pass
        elif d['status'] == 'finished':
            self.after(0, lambda: p_lbl.configure(text="下載完成！合併處理中...", text_color="#0000cd"))

if __name__ == "__main__":
    app = App()
    app.mainloop()