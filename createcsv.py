from glob import glob
from os.path import getmtime
import json
from extract import dict_files
import pandas as pd
import sys


# https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys
def flatten(ddd, parent_key=None, sep='_'):
    items = []
    for k, v in ddd.items():
        new_key = parent_key + sep + k if parent_key else k
        if type(v) == dict:
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
     

def generate_table(verbose=False):
    database_array = []
    database_json = dict_files("./json/*.json")
    # data, conteudo do json 
    for key, val in database_json.items():
        dic = json.loads(val) # convertemos em dicionário do python
        data = key.strip("./json") 
        registry =  {"data": data}
        registry.update( flatten(dic, sep="_") )
        database_array.append(registry)
    return database_array

if __name__ == "__main__":
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    if verbose:
        print("Lendo dados dos arquivos .json")
    dados = generate_table(verbose)
    if verbose:
        print("Gerando dataframe")
    df = pd.DataFrame(dados)
    df.set_index(pd.to_datetime(df.data), inplace=True)
    df.drop(columns="data", inplace=True)
    df.sort_index(inplace=True)
    taxa_ocupacao = df["leitos_SUS_ocupados"]/df["leitos_SUS_disponiveis"]
    df.insert(6, "taxa_ocupacao", taxa_ocupacao)
    if verbose:
        print("Salvando dados-consolidados.csv")
    df.to_csv("dados-consolidados.csv")
