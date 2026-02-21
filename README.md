# YouTube-Downloader
**本專案僅能在 `windows` 環境下使用**
## 本地端部屬
python套件要求請使用 `requirements.txt`    
本專案使用 yt-dlp 進行下載，為確保能順利解析 YouTube 高畫質影片 (解決 JS challenge)，請安裝 `Denoe` 並下載 `yt-dlp` 需要的破解腳本

```PowerShell
(請使用PowerShell 進行操作)
# 安裝 Deno
irm https://deno.land/install.ps1 | iex

# 設定環境變數 (執行後請重啟終端機)
$denoPath = "$HOME\.deno\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$denoPath", "User")

# 下載yt-dlp需要的破解腳本
# 如果你的 yt-dlp 是放在專案目錄下的 .exe 檔，請確保在專案根目錄執行此行
yt-dlp --remote-components ejs:github --update
```

本專案需要 `FFmpeg` 來處理影片與音訊的合併（若未安裝，將無法下載高畫質影片）：
1. 前往官網下載 [FFmpeg 執行檔](https://www.gyan.dev/ffmpeg/builds/)
2. 解壓縮後，將 `bin` 資料夾內的 `ffmpeg.exe` 路徑加入系統的 **環境變數 (Path)** 中
3. 在終端機輸入 `ffmpeg -version` 確認是否安裝成功

> **題外話：** 如果你懶得設定環境變數，也可以直接將 `ffmpeg.exe` 、 `ffplay.exe` 放在 `main.py` 的同一個資料夾下


環境完成後，執行 `main.py` 即可使用

## 使用 Setup.exe 安裝

您可以前往 [Releases 頁面](https://github.com/defineint/YouTube-Downloader/releases) 下載最新版本

> **安裝說明：**
> 1. 下載 `YouTubeDownloader_Setup.exe`
> 2. 執行安裝程式（若 Windows 彈出保護視窗，請點擊「詳細資訊」並選擇「仍要執行」）
> 3. 安裝完成後，即可從桌面捷徑啟動程式


