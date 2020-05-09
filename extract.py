from glob import glob
from os.path import getmtime
import regex
import json
from functools import reduce
import sys
import os
import shutil


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


def extract_2level_regex(pattern, text):
    """Quando tem um grupo de captura dentro do outro, 
    retorna todas as ocorrências do grupo de captura interno."""
    match = regex.search(pattern, text)
    if match:
        return match.captures(2)


def extract_regex(pattern, text):
    match = regex.search(pattern, text)
    if match:
        # retorna o primeiro grupo de captura
        return match.captures(1)[0]


def captura_internacoes(texto):
    patt = r"Internações\nem UTI\n(\n(\d+)\n){9}"
    return extract_2level_regex(patt, texto)


def captura_ventilacao(texto):
    patt = r"Ventilação\nmecânica\n(\n(\d*)\n){9}"
    return extract_2level_regex(patt, texto)


def captura_altas(texto):
    patt = r"Altas da UTI\npara enfermaria\n(\n(\d*)\n){9}"
    return extract_2level_regex(patt, texto)


def converte_testa_dados(array):
    """Nosso array de dados contém 9 números, 
    que estão distrubuídos nas seguintes colunas
    SUS | Privada | Total
    cada uma das quais tem as subcolunas
    confirmados | suspeitos | total  

    Sendo assim, vamos checar a consistência dos dados. 
    Se tudo tiver ok, retorna uma lista com números inteiros.
    Se tiver algo errado, retorna uma string indicando onde o erro ocorreu.
     """
    arrn = [int(x) for x in array]
    # testamos se a soma das categorias correspondentes está correta
    teste_colunas = [arrn[0+x] + arrn[3+x] == arrn[6+x] for x in range(3)]
    # testamos se a soma em cada subcategoria está correta
    teste_subcolunas = [arrn[3*x+0] + arrn[3*x+1]
                        == arrn[3*x+2] for x in range(3)]
    colunas_ok = reduce(lambda x, y: x and y, teste_colunas)
    subcolunas_ok = reduce(lambda x, y: x and y, teste_subcolunas)
    erros_colunas = ["confirmados", "suspeitos", "total"]
    erros_subcolunas = ["SUS", "Privado", "Totais"]
    if colunas_ok:
        if subcolunas_ok:
            return arrn
            # se tudo ok, retorna o array convertido em numeros
        else:
            i = teste_subcolunas.index(False)
            return erros_subcolunas[i]
            # se não, retorna o indice de onde deu erro
    else:
        i = teste_colunas.index(False)
        return erros_colunas[i]


def get_uti_data(text):
    sequencia_extracoes = [("internacoes", captura_internacoes),
                           ("ventilacao", captura_ventilacao),
                           ("altas_enfermaria", captura_altas)]
    dicionario = dict()
    for chave, function in sequencia_extracoes:
        dados = converte_testa_dados(function(text))
        if type(dados) == str:
            # deu ruim
            return dados
        else:
            # deu bom
            dicionario[chave] = {
                "conf": {
                    "sus": dados[0],
                    "priv": dados[3],
                    "total": dados[6]
                },
                "susp": {
                    "sus": dados[1],
                    "priv": dados[4],
                    "total": dados[7]
                }
            }
    return dicionario


def get_leitos_sus(texto):
    ocupados = int(extract_regex(r"(\d+)\nocupados", texto))
    reservados = int(extract_regex(r"(\d+)\nleitos\nreservados", texto))
    disponiveis = int(extract_regex(r"(\d+)\ndisponíveis", texto))
    if ocupados + disponiveis == reservados:
        return {"ocupados": ocupados, "reservados": reservados, "disponiveis": disponiveis}
    else:
        return "erro"


def get_testes(texto):
    testes_lacen = extract_regex(r"(\d+[\.\d{3}]*)\n\nexames", texto)
    neg = texto.count("negativo")
    proc = texto.count("processados")
    tipo = "negativos" if neg else "processados"
    testes_lacen = int(testes_lacen.replace(".", ""))
    print(testes_lacen, tipo)
    return testes_lacen, tipo


def get_confirmados(texto):
    confirmados = extract_regex(r"(\d+[\.\d{3}]*)\n\ncasos con", texto)
    return int(confirmados.replace(".", ""))


def get_obitos(texto):
    patt = r"óbitos\n(\n(\d+[\.\d{3}]*)\n){3}"
    obitos = extract_2level_regex(patt, texto)
    return obitos[-1]


def get_testes_aguardando(texto):
    regex = r"(\d+)\n\nexames\naguardando"
    testes_aguardando = extract_regex(regex, texto)
    return int(testes_aguardando)


def extraction_loop(verbose=False):
    dicionario = dict_files("./txt/*.txt")
    for caminho, conteudo in dicionario.items():
        confirmados = get_confirmados(conteudo)
        num_testes, tipo_testes = get_testes(conteudo)
        aguardando = get_testes_aguardando(conteudo)
        obitos = get_obitos(conteudo)
        conteudo_json = {"casos_conf": confirmados,
                         "obitos": obitos,
                         "testes": num_testes,
                         "teste_tipo": tipo_testes,
                         "testes_aguardando": aguardando}
        if "Internações" in conteudo:
            conteudo_json.update({
                "leitos_SUS": get_leitos_sus(conteudo),
                "UTI":  get_uti_data(conteudo),
            })
        json_path = caminho.replace("txt", "json", 2)
        if verbose:
            print(
                f"Encontrados dados em {caminho}. Extraindo para {json_path}")
        with open(json_path, "w") as fp:
            json.dump(conteudo_json, fp, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    clear = "-c" in sys.argv or "--clear" in sys.argv
    if clear:
        print("Limpando o diretório ./json/")
        shutil.rmtree("./json/")
    os.makedirs("json", exist_ok=True)
    extraction_loop(verbose)


# if __name__ == "__main__":
#     dicionario = dict_files("./txt/*.txt")
#     for caminho, conteudo in dicionario.items():
#         print(caminho, "\n", end="\t")
#         for y in ["aguardando", "MACRORREGIÃO", "SUS", "leitos", "CASOS CONFIRMADOS POR MACRORREGIÃO DE SAÚDE"]:
#             if y in conteudo:
#                 print(y, end=" ")
#         print(f"testes aguardando {a}")
