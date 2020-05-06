from glob import glob
from os.path import getmtime
import os

def convert_loop():
    lista_pdfs = sorted(glob("*.pdf"), key=getmtime)
    for arquivo in lista_pdfs:
        comando = f"pdftotext {arquivo}"
        print(f"Convertendo {arquivo}")
        os.system(comando)

if __name__ == "__main__":
    convert_loop()