from glob import glob
from os.path import getmtime

def ls(wildcard):
    "Dá um `ls wildcard` no diretório."
    return sorted(glob(wildcard), key=getmtime)

def dict_files(wildcard):
    filenames = ls(wildcard)
    dicionario = dict()
    for file in filenames:
        with open(file) as fl:
            dicionario[file] = fl.read()
    return dicionario

if __name__ == "__main__":
    dicionario = dict_files("*.txt")
    for key, val in dicionario.items():
        if "LEITOS" in val:
            print(f"Leitos in {key}")