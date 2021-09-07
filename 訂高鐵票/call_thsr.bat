@echo off
call h:
call H:\Programming\Anaconda\Scripts\activate.bat H:\Programming\Anaconda
call conda activate THSR
call cd H:\Programming\THSR\訂高鐵票
call python thsr_ticket\main.py
