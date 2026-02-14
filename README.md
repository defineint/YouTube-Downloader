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

完成環境部屬後，執行 `main.py` 即可使用

## 使用執行檔

在本地新建資料夾並關閉該資料夾的防毒偵測，避免執行檔被防毒刪除，請用 `PowerShell` 並以**管理員權限**執行以下指令  
資料夾關閉防毒後請自行注意安全性
```PowerShell
# 選擇資料夾名稱跟路徑
$fullPath = "填入資料夾路徑 (EX: C:\Users\Deskop\newfolder)"

# 建立資料夾
New-Item -Path $fullPath -ItemType Directory

# 將路徑加入 Windows Defender 的排除清單
Add-MpPreference -ExclusionPath $fullPath

# 查詢目前的排除路徑清單(檢測用)
(Get-MpPreference).ExclusionPath
```

下載 `YTDL.zip` 檔案 **(解壓碼：1234)**: [https://drive.google.com/file/d/1v9HUMseM3FLT7CSrrNp-COxsb7nkS8Au/view?usp=sharing](https://drive.google.com/file/d/1v9HUMseM3FLT7CSrrNp-COxsb7nkS8Au/view?usp=sharing)  
將壓縮檔解壓到剛剛建立的資料夾中，以管理員權限執行 `Yt_Downloader.exe` 即可使用


