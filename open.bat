@echo off
start python main.py
timeout /t 5 /nobreak
start http://localhost:5000