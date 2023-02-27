import  subprocess
import os
import tkinter






interpreter = 'python3' if os.name == 'posix' else 'python'
args = [interpreter, 'main.py', '--code', '0', '--m', 'None', '--a', '']
subprocess.Popen(args)