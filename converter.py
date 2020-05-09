import os
from glob import glob
from os.path import getmtime

import click

from cli import common_options
from utils import create_directory


@click.command()
@common_options
def convert_loop(clear, verbose):
    create_directory("txt", clear)
    lista_pdfs = sorted(glob("./pdf/*.pdf"), key=getmtime)
    for arquivo in lista_pdfs:
        txt_path = arquivo.replace("pdf", "txt", 2)
        comando = f"pdftotext {arquivo} {txt_path}"
        if verbose:
            print(f"Convertendo {arquivo}")
        os.system(comando)


if __name__ == "__main__":
    convert_loop()
