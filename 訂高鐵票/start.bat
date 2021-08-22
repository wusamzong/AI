@echo off
set condaRoot=H:\Programming\Anaconda
call %condaRoot%\Scripts\activate.bat %condaRoot%
call conda activate THSR
call cd H:\Programming\THSR\訂高鐵票
call python thsr_ticket\main.py
pause