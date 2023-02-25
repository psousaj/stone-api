import logging

classe = ''

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Criando um handler para o log no terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Criando um handler para o log em arquivo de texto
file_handler = logging.FileHandler('logs.txt')
file_handler.setLevel(logging.DEBUG)

# Definindo o formato das mensagens de log
formatter = logging.Formatter('%(asctime)s - %(name)s -%(levelname)s- %(message)s'.format(classe), datefmt='%d/%m/%Y|%H:%M:%S')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Adicionando os handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)