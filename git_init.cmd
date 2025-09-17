@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
cd /d %~dp0
git init
git add .
git -c user.name="Fecart" -c user.email="fecart@example.com" commit -m "Initial commit: Flask app + SQLite + init_db + README + gitignore"
exit /b 0


