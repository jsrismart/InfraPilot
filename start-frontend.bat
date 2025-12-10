@echo off
cd /d "C:\Users\SridharJayaraman\Downloads\infrapilot 2\infrapilot\frontend\dist"
python -m http.server 3001 --bind 0.0.0.0
pause
