import  os

desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop') if os.name == "nt" else os.path.join(os.environ['HOME'], 'Área de Trabalho')
print(f"aqui: {desktop}")