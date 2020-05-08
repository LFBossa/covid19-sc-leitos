from glob import glob
from os.path import getmtime
import os, sys, shutil

def convert_loop(verbose=False):
    lista_pdfs = sorted(glob("./pdf/*.pdf"), key=getmtime)
    for arquivo in lista_pdfs:
        txt_path = arquivo.replace("pdf", "txt", 2)
        comando = f"pdftotext {arquivo} {txt_path}"
        if verbose:
            print(f"Convertendo {arquivo}")
        os.system(comando)


if __name__ == "__main__":
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    clear = "-c" in sys.argv or "--clear" in sys.argv
    if clear:
        print("Limpando o diretório ./txt/")
        shutil.rmtree("./txt/")
    os.makedirs("txt", exist_ok=True)
    convert_loop(True)