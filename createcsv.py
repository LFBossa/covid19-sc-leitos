import json

import click
import pandas as pd

from extract import dict_files


# https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys
def flatten(ddd, parent_key=None, sep="_"):
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
        dic = json.loads(val)  # convertemos em dicionário do python
        data = key.strip("./json")
        registry = {"data": data}
        registry.update(flatten(dic, sep="_"))
        database_array.append(registry)
    return database_array


@click.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default="dados-consolidados.csv",
    help="Caminho para o arquivo csv",
)
@click.option(
    "-v", "--verbose", is_flag=True, help="Exibe mensagem com progresso do script"
)
def json_to_csv(output, verbose):
    if verbose:
        print("Lendo dados dos arquivos .json")
    dados = generate_table(verbose)
    if verbose:
        print("Gerando dataframe")
    df = pd.DataFrame(dados)
    df.set_index(pd.to_datetime(df.data), inplace=True)
    df.drop(columns="data", inplace=True)
    df.sort_index(inplace=True)
    taxa_ocupacao = df["leitos_SUS_ocupados"] / df["leitos_SUS_disponiveis"]
    df.insert(6, "taxa_ocupacao", taxa_ocupacao)
    if verbose:
        print(f"Salvando {output}")
    df.to_csv(output)


if __name__ == "__main__":
    json_to_csv()
