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

    def build_ydl_opts(self, **extra):
        # 解析跟下載共用同一份基礎設定，兩邊才不會用不同的 client 打 YouTube
        opts = {
            'quiet': True,
            'nocolor': True,
            'noplaylist': True,
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'js_runtimes': {'deno': {}},
            'remote_components': ['ejs:github'],
        }
        opts.update(extra)
        return opts

    def find_downloaded_file(self, ydl, info):
        # 用 yt-dlp 自己算出來的檔名去比對，標題含特殊字元被消毒過也對得上；
        # 副檔名不限，所以 Audio Only 存成 .mp3 一樣抓得到
        try:
            stem = os.path.splitext(os.path.basename(ydl.prepare_filename(info)))[0]
        except Exception:
            return None
        if not stem:
            return None
        for name in os.listdir(self.download_path):
            root, ext = os.path.splitext(name)
            if root == stem and ext.lower() not in ('.part', '.ytdl', '.temp'):
                return name
        return None

    def analyze_thread(self, video_url, ui_components):
        (p_bar, p_lbl, t_lbl, img_lbl, res_combo, dl_btn) = ui_components

        try:
            self.after(0, lambda: p_lbl.configure(text="正在獲取影片資訊...", text_color="#0000cd"))

            with yt_dlp.YoutubeDL(self.build_ydl_opts()) as ydl:
                info = ydl.extract_info(video_url, download=False)
                video_title = info.get('title', 'Unknown Tittle')
                self.after(0, lambda: t_lbl.configure(text=f"{video_title[:20]}..."))

                if self.find_downloaded_file(ydl, info):
                    self.after(0, lambda: p_lbl.configure(text="提示：此影片已經下載過啦！", text_color="red"))
                    self.after(0, lambda: dl_btn.configure(text="None", state="disabled", fg_color="gray"))

                    self.get_thumbnail(info.get('thumbnail'), img_lbl)
                    self.active_tasks.remove(video_url)
                    return
                
                # file not exist, so download it.

                self.get_thumbnail(info.get('thumbnail'), img_lbl)

                formats = info.get('formats', [])
                quality_map = {}

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

                        label = f"{std_h}p{fps}" if fps > 30 else f"{std_h}p"

                        # 直式和超寬影片的 height 跟標籤數字對不上，必須記下實際 height，
                        # 下載時才選得到正確檔位。同一標籤可能涵蓋多種 fps
                        #（例如 144p 有 15 和 30），等高時取較高的那個
                        known = quality_map.get(label)
                        if known is None or (h, fps) > (known['height'], known['fps']):
                            quality_map[label] = {'height': h, 'fps': fps, 'std_h': std_h}

                sorted_quality = sorted(
                    quality_map.items(),
                    key=lambda kv: (kv[1]['std_h'], kv[1]['fps']),
                    reverse=True
                )

                res_options = [label for label, _ in sorted_quality]
                res_options.append("Audio Only")

                def update_ui_ready():
                    res_combo.configure(values=res_options, state="normal")
                    if res_options:
                        res_combo.set(res_options[0])
                    p_lbl.configure(text="解析完成，請選擇畫質", text_color="green")
                    dl_btn.configure(text="下載", state="normal")
                    dl_btn.configure(command=lambda: self.start_download(video_url, ui_components, quality_map))
            
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

    def start_download(self, video_url, ui_components, quality_map):
        (p_bar, p_lbl, t_lbl, img_lbl, res_combo, dl_btn) = ui_components
        selected_res = res_combo.get()

        if not selected_res:
            return

        dl_btn.configure(state="disabled", text="下載中...")
        res_combo.configure(state="disabled")

        def run_download():
            try:
                ydl_opts = self.build_ydl_opts(
                    progress_hooks=[lambda d: self.update_progress(d, p_bar, p_lbl)],
                    sleep_interval=3,
                    max_sleep_interval=5,
                )

                if selected_res == "Audio Only":
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                else:
                    quality = quality_map.get(selected_res)
                    if quality:
                        # 用解析時記下的實際 height，而不是標籤上的數字
                        limit = f"[height<={quality['height']}][fps<=?{quality['fps']}]"
                    else:
                        limit = f"[height<={selected_res.split('p')[0]}]"

                    # mp4 容器優先配 m4a，避免 opus-in-mp4 在部分播放器和剪輯軟體打不開
                    ydl_opts['format'] = (
                        f'bestvideo{limit}+bestaudio[acodec^=mp4a]/'
                        f'bestvideo{limit}+bestaudio/'
                        f'best{limit}'
                    )
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