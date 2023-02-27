import  subprocess
import os
import tkinter as tk
# from tkinter import *
from tkinter.ttk import * 

root = tk.Tk()
root.geometry('250x200')
root.title("Stone API - Connection")

root.rowconfigure([1], weight=1, minsize=1)
root.columnconfigure([1], weight=1, minsize=1)

txt1 = tk.Label(text="Digite o código do cliente", height=1).grid(row=0, column=0, sticky="NSEW")

cod = tk.Entry().grid(row=0, column=1, sticky="NSEW")

def bora():
    print(cod.get())

btn = Button(root, text='Baixar', command = bora).grid(row=1, column=0)






root.mainloop()

# interpreter = 'python3' if os.name == 'posix' else 'python'
# args = [interpreter, 'main.py', '--code', '0', '--m', 'None', '--a', '']
# subprocess.Popen(args)