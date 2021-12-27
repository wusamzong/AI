@echo off
call h:
call H:\Programming\01_Software\Anaconda\Scripts\activate.bat H:\Programming\01_Software\Anaconda
call conda activate THSR
call cd H:\Programming\04_Tools_Python\THSR\訂高鐵票
call python thsr_ticket\main.py
pause