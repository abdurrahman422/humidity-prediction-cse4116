@echo off
cd /d "%~dp0"
python humidity_server.py --open
if errorlevel 1 (
  echo App could not start. Check the message above. If port 8765 is already in use, open http://127.0.0.1:8765
  pause
)
