@echo off
title Fists - YouTube Video Downloader
color E & echo [!] - Installation is started...
timeout /t 2 /nobreak > nul
color 6 & py -m pip install -r requirements.txt
timeout /t 2 /nobreak > nul
cls
color A & echo [+] - Installation completed.
pause