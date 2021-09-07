from subprocess import Popen
import time
import os

while True:
    # subprocess.Popen('cmd /c start call_thsr.bat')
    p = Popen("call_thsr.bat", cwd=r"H:\Programming\THSR\訂高鐵票")
    stdout, stderr = p.communicate()
    p.kill()

# subprocess.Popen('cmd /c start call_thsr.bat')
# subprocess.Popen('cmd /c pause')