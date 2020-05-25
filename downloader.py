import datetime as dt
import os
import shutil
from urllib.request import urlretrieve

import click

from cli import common_options
from utils import create_directory


def get_link_from_isostring(date):
    ano, mes, dia = date.isoformat().split("-")
    return f"https://www.coronavirus.sc.gov.br/wp-content/uploads/{ano}/{mes}/boletim-epidemiologico-{dia}-{mes}-{ano}.pdf"


def download_if_inexistent(date):
    date_iso = date.isoformat()
    date_br = date.strftime("%d/%m/%y")
    caminho = f"./pdf/{date_iso}.pdf"

    if os.path.exists(caminho):
        return f"Relatório do dia {date_br} já existe"
    else:

        link1 = get_link_from_isostring(date)
        link2 = link1.replace("2020/04", "2020/05")
        link3 = link1.replace("boletim", "Boletim") # sim mudaram isso
        sequencia = [link1, link2, link3]
        i = 0
        for link in sequencia:
            try:
                urlretrieve(link, filename=caminho)
            except:  
                i = i + 1
                print(f"Erro com link{i}")
                continue                
            else:
                return f"Baixando relatório do dia {date_br}"
                


@click.command()
@common_options
def download_loop(clear, verbose):
    create_directory("pdf", clear)

    INICIO = dt.date(2020, 4, 14)
    numero_dias = (INICIO.today() - INICIO).days
    for n in range(numero_dias):
        data = INICIO + dt.timedelta(n)
        msg = download_if_inexistent(data)
        if verbose:
            print(msg)


if __name__ == "__main__":
    download_loop()
