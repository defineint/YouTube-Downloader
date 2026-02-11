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
        self.button = customtkinter.CTkButton(self.input_frame, text="下載", command=self.check_button_event)
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

        title_label = customtkinter.CTkLabel(dl_task_frame, text=f"解析中：{url[:30]}...", anchor="w", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w")

        status_label = customtkinter.CTkLabel(dl_task_frame, text="等待下載...", anchor="w", text_color="#0000cd", font=("Arial", 14))
        status_label.grid(row=1, column=1, sticky="w")

        progress_bar = customtkinter.CTkProgressBar(dl_task_frame)
        progress_bar.grid(row=2, column=0, columnspan=2, padx=0, pady=10, sticky="ew")
        progress_bar.set(0)

        #multithreading
        def download_thread(video_url, vd_components):
            (p_bar, p_lbl, t_lbl, img_lbl) = vd_components
            # 防止重複下載
            with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
                try:
                    info = ydl.extract_info(video_url, download=False)
                    title = info.get('title', 'video')
                    file_path = os.path.join(self.download_path, f"{title}.mp4")

                    if os.path.exists(file_path):
                        self.after(0, lambda: p_lbl.configure(text="提示：此影片已下載過囉！", text_color="red"))
                        self.after(0, lambda: t_lbl.configure(text=title))
                        self.active_tasks.remove(video_url)
                        return 
                except:
                    pass
            def progress_hook(d):
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
                            
                    except Exception as e:
                        print(f"計算錯誤: {e}")
                elif d['status'] == 'finished':
                    self.after(0, lambda: p_lbl.configure(text="下載完成！合併處理中...", text_color="green"))

            ydl_opts = {
                'js_runtime': 'deno',
                'remote_components': ['ejs:github'],
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
                'format': 'bestvideo[vcodec^=avc]+bestaudio[acodec^=mp4a]/best[ext=mp4]/best',
                'noplaylist': True,
                'merge_output_format': 'mp4',
                'progress_hooks': [progress_hook],
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'nocolor': True,
                'quiet': True
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.after(0, lambda: p_lbl.configure(text="正在獲取影片資訊..."))
                    info = ydl.extract_info(video_url, download=False)

                    video_title = info.get('title', 'unknow title')
                    self.after(0, lambda: t_lbl.configure(text=video_title))

                    pict_url = info.get('thumbnail')
                    if pict_url:
                        try:
                            response = requests.get(pict_url, stream=True)
                            img_data = Image.open(BytesIO(response.content))
                            ctk_img = customtkinter.CTkImage(light_image=img_data, dark_image=img_data, size=(160, 90))
                            self.after(0, lambda: img_lbl.configure(image=ctk_img, text=""))
                        except Exception as e:
                            print("picture loading is fail.")
                    
                    self.after(0, lambda: p_lbl.configure(text="開始下載..."))
                    ydl.download([video_url])
                    
                    self.after(0, lambda: p_lbl.configure(text="完成!"))
            except Exception as e:
                self.after(0, lambda: p_lbl.configure(text=f"錯誤: {str(e)}", text_color="red"))
            finally:    
                self.active_tasks.remove(video_url)
        vd_pack = (progress_bar, status_label, title_label, pict_label)
        thread = threading.Thread(target=download_thread, args=(url, vd_pack))     
        thread.daemon = True
        thread.start()
        
        self.task_count += 1
        self.entry.delete(0, "end")

if __name__ == "__main__":
    app = App()
    app.mainloop()