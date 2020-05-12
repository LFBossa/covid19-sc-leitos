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
        link = get_link_from_isostring(date)
        try:
            urlretrieve(link, filename=caminho)
        except:
            try:
                # obrigado governo do estado por colocar o relatório do dia
                # 29/04 na pasta de maio
                link = link.replace("2020/04", "2020/05")
                urlretrieve(link, filename=caminho)
            except: 
                return f"Falha ao baixar relatório do dia {date_br}"
            else:
                return f"Baixando relatório do dia {date_br}"
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
