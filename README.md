# YouTube-Downloader
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
yt-dlp --remote-components ejs:github --update
```




