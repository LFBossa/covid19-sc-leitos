import datetime as dt 
from urllib.request import urlretrieve
import os, sys, shutil

def get_link_from_isostring(date):
    ano, mes, dia = date.isoformat().split("-")
    URL = f"https://www.coronavirus.sc.gov.br/wp-content/uploads/{ano}/{mes}/boletim-epidemiologico-{dia}-{mes}-{ano}.pdf"
    return URL #.format(ano=ano, mes=mes, dia=dia)

def download_if_inexistent(date):
    date_iso = date.isoformat()
    date_br = date.strftime('%d/%m/%y')
    caminho = f"./pdf/{date_iso}.pdf"

    if os.path.exists(caminho):
        return f"Relatório do dia {date_br} já existe"
    else:
        link = get_link_from_isostring(date)
        urlretrieve(link, filename=caminho)
        return f"Baixando relatório do dia {date_br}"

def download_loop(verbose=False):
    INICIO = dt.date(2020,4,14)
    numero_dias = (INICIO.today() - INICIO).days
    for n in range(numero_dias):
        data = INICIO + dt.timedelta(n)
        msg = download_if_inexistent(data)
        if verbose:
            print(msg)
        

if __name__ == "__main__":
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    clear = "-c" in sys.argv or "--clear" in sys.argv
    if clear:
        print("Limpando o diretório ./pdf/")
        shutil.rmtree("./pdf/")
    os.makedirs("pdf", exist_ok=True)    
    download_loop(verbose)