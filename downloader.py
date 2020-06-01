import datetime as dt
import os
import shutil
from urllib.request import urlretrieve

import click

from cli import common_options
from utils import create_directory


def get_links_from_date(date):
    # O ultimo relatório do mês é publicado no mês seguinte 
    ano, mes, dia = date.isoformat().split("-")
    amanha = date + dt.timedelta(1)
    prox_mes = amanha.isoformat().split("-")[1]
    template = f"https://www.coronavirus.sc.gov.br/wp-content/uploads/{ano}/{{mes0}}/boletim-epidemiologico-{dia}-{mes}-{ano}.pdf"
    return template.format(mes0=mes), template.format(mes0=prox_mes)


def download_if_inexistent(date):
    date_iso = date.isoformat()
    date_br = date.strftime("%d/%m/%y")
    caminho = f"./pdf/{date_iso}.pdf"

    if os.path.exists(caminho):
        return f"Relatório do dia {date_br} já existe"
    else:

        link1, link2 = get_links_from_date(date) 
        boletim = lambda x: x.replace("boletim", "Boletim") # sim mudaram isso
        link3, link4 = (boletim(x) for x in [link1, link2])
        sequencia = [link1, link2, link3, link4]
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
