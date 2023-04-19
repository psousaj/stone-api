
import os
import sys
import threading
import  subprocess
import tkinter as tk
from tkinter import *
from configs.logging_config import Logger

class ThreadedTask(threading.Thread):
    def __init__(self, callback, args):
        threading.Thread.__init__(self)
        self.callback = callback
        self.args = args
        self.logger = Logger(__name__).logger

    def run(self):
        args = self.args
        meses = {
            "janeiro": "1",
            "fevereiro": "2",
            "março": "3",
            "abril": "4",
            "maio": "5",
            "junho": "6",
            "julho": "7",
            "agosto": "8",
            "setembro": "9",
            "outubro": "10",
            "novembro": "11",
            "dezembro": "12"
        }
        args[5] = meses.get(str(args[5]).lower())
        print("AQUIII", args[5])
        print("ARGS", args)

        try:
            # thread = threading.Thread(target=subprocess.Popen, args=(args,))
            subprocess.Popen(args)
            # thread.start()
            # thread.join()
        except Exception:
            self.logger.error("Ocorreu um erro, verifique os logs e tente novamente")
            sys.exit()

        self.callback()

class App:
    def __init__(self, master):
        self.master = master
        self.bg = PhotoImage(file=r"{}\assets\background.png".format(os.getcwd()))
        self.bg_label = Label(self.master, image=self.bg)
        self.button = Button(self.master, text="Buscar", bg="#0FCF5F", fg="white", command=self.start_task)
        self.string_var= " "
        self.mes= " "
        self.ano= " "

        # Cria a janela principal
        master = self.master
        master.geometry("584x570")
        master.title("EMS - Extrato Maquinetas Stone")

        # Carrega a imagem de fundo
        # bg_image = self.bg

        # Adiciona a imagem de fundo à janela usando o método place
        bg_label = self.bg_label
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Adiciona um label ao frame
        self.string_var = StringVar()
        label = Entry(master, bg="#ffffff", textvariable=self.string_var)
        label.place(relx=0.34672, rely=0.38)
        label.config(width=17, font=("Poppins", 20))


        # lista de meses
        meses = ['Selecione', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

        # variável para armazenar o mês selecionado
        self.mes = StringVar(master)
        self.mes.set(meses[0])  # seta o valor inicial

        # cria o dropdown
        dropdown = OptionMenu(master, self.mes, *meses)
        dropdown.place(relx=0.34672, rely=0.48)
        dropdown.config(width=18, height=1, font=("Poppins", 16))


        # lista de meses
        anos = list(range(2015, 2024))

        # variável para armazenar o mês selecionado
        self.ano = StringVar(master)
        self.ano.set(meses[0])  # seta o valor inicial

        # cria o dropdown
        dropdown_ano = OptionMenu(master, self.ano, *anos)
        dropdown_ano.place(relx=0.34672, rely=0.59) if not master.size()[1] > 500 else dropdown_ano.place(relx=0.34672, rely=1)
        dropdown_ano.config(width=18, height=1, font=("Poppins", 16))

        # def init_program():
        #     args = ['python', 'main.py', '--cnpj', f'{string_var.get()}', '--mes', f'{mes_selecionado.get()}', '--ano', f'{ano.get()}']
        #     thread = threading.Thread(target=sub_process, args=(args,))
        #     thread.start()
        #     thread.join() # espera a thread terminar

        self.button.config(font=("Poppins", 14))
        self.button.place(relx="0.659", rely="0.679")

        master.maxsize(584, 570)
        master.minsize(584, 565)

    def start_task(self):
        self.button["state"] = "disabled"
        args = ['python', 'main.py', '--cnpj', f'{self.string_var.get()}', '--mes', f'{self.mes.get()}', '--ano', f'{self.ano.get()}']
        self.thread = ThreadedTask(self.task_finished, args)
        self.thread.start()
        self.thread.join()

    def task_finished(self):
        self.button["state"] = "normal"
        print("Tarefa Finalizada", "A tarefa foi finalizada com sucesso")
# CNPJ 41474152000103

root = tk.Tk()
app = App(root)
root.mainloop()