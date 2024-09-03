@echo off
call conda activate base
cd "%~dp0"
python "./window_manager.py"
