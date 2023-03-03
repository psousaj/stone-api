import os
import json
from datetime import datetime
import xml.etree.ElementTree as ET

def replace_string(date:datetime, export=False):
    """Informa o final do arquivo (replace removido na verificação se o diretório existe)

    Args:
        - date (datetime): data
        - extension (str): extensão do path para o arquivo desejado
        - access_path (bool, optional): especifica se é para um path do diretório de access. Defaults to False.
        - code (int, optional): código do cliente. Defaults to 0.

    Returns:
        - str: trecho final do path que vai ser removido na verificaçao se o diretório existe
    """
    return r'extrato-{}.xml'.format(date.day) if not export else r'relatorio-{}.xlsx'.format(date.strftime("%B"))

def isUnix(path, **kwargs):
    """Gera um path modificado para cada s.o, aumentando a compatibilidade

    Returns:
      - {str}: path
    """
    refactored_path = path.replace('\\', '/') if (os.name == "posix") else path
    refactored_path += refactored_path.join([f"{value}" for value in kwargs.items()])
    return refactored_path

def path_exists(path_and_replace):
    """Essa classe verifica se o diretório já existe e o cria caso não exista.
    Recebe tanto uma tupla (retono de getPath()), quanto um path direto

    Returns:
      - {str}: path completo
    """
    path = ""
    replace = ""
    if isinstance(path_and_replace, tuple):
        path = isUnix(path_and_replace[0])
        replace = isUnix(path_and_replace[1])

        if not os.path.exists(path):
                os.makedirs(path)

        return path+replace
    
    path = isUnix(path_and_replace)
    if not os.path.exists(path):
        os.makedirs(path)
    
    return path

def getPath(code:int, date:datetime, extension:str, complete=False, create_if_not_exists=False, export_path=False, empresa=None) -> str:
        """
        Gera o path_file do arquivo solicitado, e retorna uma tupla ou uma string 
        dependendo do parâmetro complete. Caso o complete seja False, retornará uma tupla (path, replace)

        Args:
           - code: (int) código da empresa
           - date: (datetime) data inicial solicitada
           - extension: (str) extensao do arquivo
           - complete: (boolean, optional) certifica o retorno do método como descrito
            - create_if_not_exists: (boolean, optional) se informado como True, verifica o diretório e o cria
        
        Returns:
            Sempre string, porém em 2 tipos distintos
            - { tuple } -> (path, replace)
            - { str } -> path
        """
        path = os.getcwd()
        if export_path:
            path += r'\connection\files\{}\{}\relatorio-stone-{}.{}'.format(empresa,
                                                                    date.strftime('%Y'),
                                                                    date.strftime('%B'),
                                                                    extension)
            replace = replace_string(date, export=True)
            path = path.replace(replace, "")
            path = format_export(path, empresa)
        else:
            path += r'\connection\files\{}\{}\{}-{}\extrato-{}.{}'.format(code,
                                                                        date.strftime('%Y'),
                                                                        date.strftime('%m'),
                                                                        date.strftime('%B'),
                                                                        date.day,
                                                                        extension)
            replace = replace_string(date)
            path = path.replace(replace, "")
            
        path = isUnix(path)
        replace = isUnix(replace)

        if create_if_not_exists:
            path_exists(path)

        if complete:
            return path+replace
        
        return path, replace


def get_config_path():
    """Localiza o arquivo com as credenciais de acesso informado pela equipe da API

    Returns:
        - str: path completo do arquivo de configuração json
    """
    path = os.getcwd()
    path += r'\configs\stone-credentials.json'
    path = isUnix(path)
    return path

def save_xml(path:str, object):
    """Salva o xml em local especificado por parâmetro

    Args:
       - path (str): caminho onde salva o arquivo
       - object (xml): xml com os dados
    """
    with open(path, 'w') as file:
        file.write(object)

def load_json(path:str):
    """transforma um dicionário em json e o retorna

    Args:
        - object (dict): dicionário com os dados

    Returns:
        - json: json
    """
    with open(path, 'r') as file:
        data = json.load(file)
    return data

def load_xml(path:str):
    """lê e retorna um xml pelo path especificado por parâmetro

    Args:
        - path (str): caminho para o xml

    Returns:
        - {xml}: xml
    """
    data = ET.parse(path).getroot()
    return data

def is_future_date(date:datetime):
    """verifica se é uma data futura, o que geraria um erro na requisiçao,
    ja que o arquivo seria inexistente

    Args:
        - date (datetime): data em formato datetime

    Raises:
        - ResourceWarning: Mensagem de erro
    """
    if date.month > datetime.now().month:
        raise ResourceWarning("Data futura. impossível acessar arquivo")

def format_export(path:str, empresa:str) -> str:
    """
    Faz a validação e mudança para o diretório correto do arquivo excel exportado

    Returns: 
       - path completo para exportar .xlsx
    """
    path = path.replace("connection", "vendas")
    return path

def find_desktop_path():
    """Busca o caminho da área de trabalho do desktop independente do s.o

    Returns:
        str: path com o caminho para o desktop
    """
    if os.name == "posix":
       return os.path.join(os.environ['HOME'], 'Área de Trabalho')
    return os.path.join(os.environ['USERPROFILE'], 'Desktop')   

# def init_liberation():
#     """
#     Verifica se o arquivo com os dados do cliente informado existe.
#     Caso contrário, encerra o programa
#     """
#     try:
#         path = getPath()
#         load_json(path)
#     except ImportError:
#         logger.error("Arquivo com companyNumber e infos inexistente")
#         time.sleep(5)
#         sys.exit()
    
    