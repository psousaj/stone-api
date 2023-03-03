
from tkinter import *
import tkinter

master = Tk()
# Cria a janela principal
master = master
master.geometry("584x570")
master.title("EMS - Extrato Maquinetas Stone")

# Carrega a imagem de fundo
bg_image = PhotoImage(file=r"C:\Users\TAX Contabilidade\Desktop\background.png")

# Adiciona a imagem de fundo à janela usando o método place
bg_label = Label(master, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# # Cria um frame para adicionar outros widgets
# frame = master.Frame(master, bg="#eee")
# frame.place(relx=0.5, rely=0.1, relwidth=0.75, relheight=0.8, anchor='n')
# frame.attributes("-alpha", 0.5)

# Adiciona um label ao frame
label = Entry(master, bg="#ffffff")
label.place(relx=0.34672, rely=0.4851)
label.config(width=17, font=("Poppins", 20))

# lista de meses
meses = ['Selecione', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
         'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

# variável para armazenar o mês selecionado
mes_selecionado = StringVar(master)
mes_selecionado.set(meses[0])  # seta o valor inicial

# cria o dropdown
dropdown = OptionMenu(master, mes_selecionado, *meses)
dropdown.place(relx=0.34672, rely=0.582)
dropdown.config(width=18, height=1, font=("Poppins", 16))


# lista de meses
anos = list(range(2015, 2024))

# variável para armazenar o mês selecionado
ano = StringVar(master)
ano.set(meses[0])  # seta o valor inicial

# cria o dropdown
dropdown_ano = OptionMenu(master, ano, *anos)
dropdown_ano.place(relx=0.34672, rely=0.6907) if not master.size()[1] > 500 else dropdown_ano.place(relx=0.34672, rely=1)
dropdown_ano.config(width=18, height=1, font=("Poppins", 16))

btn = Button(master, text="Buscar", bg="#0FCF5F", fg="white") #, width=345, height=448
btn.config(font=("Poppins", 15))
btn.place(relx="0.659", rely="0.784")

master.maxsize(584, 570)
master.minsize(584, 565)
master.mainloop()
