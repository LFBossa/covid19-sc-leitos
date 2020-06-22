import json
from functools import reduce
from glob import glob
from os.path import getmtime

import click
import regex

from cli import common_options
from utils import create_directory


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
    else:
        return None


def extract_regex(pattern, text):
    match = regex.search(pattern, text)
    if match:
        # retorna o primeiro grupo de captura
        return match.captures(1)[0]
    else:
        return None


def captura_internacoes(texto):
    patt = r"Internações( em\n|\nem )UTI\n(\n(\d+)\n){9}"
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
    teste_colunas = [arrn[0 + x] + arrn[3 + x] == arrn[6 + x]
                     for x in range(3)]
    # testamos se a soma em cada subcategoria está correta
    teste_subcolunas = [
        arrn[3 * x + 0] + arrn[3 * x + 1] == arrn[3 * x + 2] for x in range(3)
    ]
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
    sequencia_extracoes = [
        ("internacoes", captura_internacoes),
        ("ventilacao", captura_ventilacao),
        ("altas_enfermaria", captura_altas),
    ]
    dicionario = dict()
    for chave, function in sequencia_extracoes:
        try:
            dados = converte_testa_dados(function(text))
            if type(dados) == str:
                # deu ruim
                return dados
            else:
                # deu bom
                dicionario[chave] = {
                    "conf": {"sus": dados[0], "priv": dados[3], "total": dados[6]},
                    "susp": {"sus": dados[1], "priv": dados[4], "total": dados[7]},
                }
        except:
            # inferno de governoooo para de mudar o pdf
            print(f"Faltam informações de {chave}")
    return dicionario


def parse_int(txt):
    try:
        return int(txt)
    except:
        return txt


def get_leitos_sus(texto):
    regex_dict = {
        "ocupados": r"(\d+)\nocupados",
        "reservados": r"(\d+)\nleitos\nreservados",
        "disponiveis": r"(\d+)\n(disponíveis|livres)",
        "totais": r"(\d+)\nleitos(\n| )totais",
        "outras_doencas": r"(\d+)\nocupados( por\noutras|\npor outras)\nenfermidades"
    }
    extracted_dict = {key: parse_int(extract_regex(val, texto))
                      for (key, val) in regex_dict.items()}
    return extracted_dict


def get_testes(texto):
    testes_lacen = extract_regex(r"(\d+[\.\d{3}]*)[\n]{1,2}exames", texto)
    testes_lacen_complex = extract_2level_regex(
        r"((\d+[\.\d{3}]*)[\n]){2}exames", texto)

    if "TESTES REALIZADOS" in texto:
        tipo = "PCR"
        testes_lacen = extract_regex(r"(\d+[\.\d{3}]*)\nPCR", texto)
        rapido = extract_regex(r"(\d+[\.\d{3}]*)\ntestes\nrápidos", texto)
        testes_lacen = int(testes_lacen.replace(".",""))
        rapido = int(rapido.replace(".",""))
        totais = testes_lacen + rapido 
    elif testes_lacen_complex:
        testes_lacen, rapido = [
            parse_int(x.replace(".", "")) for x in testes_lacen_complex]
        tipo = "PCR"
        totais = testes_lacen + rapido
    else:
        neg = texto.count("negativo")
        proc = texto.count("processados")
        tipo = "negativos" if neg else "processados"
        rapido = extract_regex(
            r"(\d+[\.\d{3}]*)\n{1,2}testes( |\n)rápidos", texto)
        testes_lacen = parse_int(testes_lacen.replace(".", ""))
        if "PCR" in texto:
            tipo = "PCR"
            rapido = parse_int(rapido.replace(".", ""))
            totais = testes_lacen + rapido
        else:
            totais = testes_lacen
    # sem a menor condições, pqp
    testes_ = extract_regex(r"(\d+ mil)\(total\)\nprocessados", texto)
    if testes_:
        testes_lacen = parse_int(
            float(testes_.replace(" ", "").replace("mil", "e3")))
        return {"lacen": testes_lacen}
    return {"totais": totais, "tipo": tipo, "lacen": testes_lacen, "rapido": rapido}


def get_confirmados(texto):
    if "casos por 100 mil" in texto: # condição para 06/06
        patt1 = r"((\d+[\.\d{3}]*)\n{2}){2}\d+,\d+\n\ncasos con"
        patt2 = r"(\n(\d+[\.\d{3}]*)\n){2}\ncasos con"
        array1 = extract_2level_regex(patt1, texto)
        array2 = extract_2level_regex(patt2, texto)
        if array1:
            confirmados = array1[0]
        elif array2:
            confirmados = array2[0]
    elif "casos ativos" in texto:
        array = extract_2level_regex(
            r"(\n(\d+[\.\d{3}]*)\n){2}\ncasos con", texto)
        confirmados = array[0]
    else:
        confirmados = extract_regex(r"(\d+[\.\d{3}]*)\n\ncasos con", texto)
    return int(confirmados.replace(".", ""))


def get_obitos(texto):
    patterns = [r"óbitos\n(\n(\d+[\.\d{3}]*)\n){3,4}",  # obrigado por mudar o padrão DE NOVO
                r"casos ativos\n(\n(\d+[\.\d{3}]*)\n){3}",
                r"(\n(\d+[\.\d{3}]*)\n){2}\n\d,\d{2}%\n\nóbitos",
                r"(\n(\d+[\.\d{3}]*)\n){2}\nóbitos"] # adicionado 20/06
    obitos = [extract_2level_regex(x, texto) for x in patterns]
    posicoes = [-1, -1, 0, 0]
    for obito, i in zip(obitos, posicoes):
        if obito:  # Obrigado governo por ter mudado o padrão
            retorno = obito[i].replace(".", "")
            return int(retorno)


def get_testes_aguardando(texto):
    # obrigado gobierno
    # 23/05 que inferno
    patterns_n_functions = [
        (r"(\d+[\.\d{3}]*)[\n]{1,2}exames aguardando", extract_regex),
        (r"((\d+[\.\d{3}]*)\n){1,2}\nexames\naguardando", extract_2level_regex),
        (r"exames\n(\d+[\.\d{3}]*)\naguardando", extract_regex),
        (r"aguardando\n(\d+[\.\d{3}]*)\nresultado", extract_regex),
        (r"aguardando\n(\d+[\.\d{3}]*)\(Lacen\)\nresultado", extract_regex),
        (r"(\d+[\.\d{3}]*)\nexames\n\nexames aguardando", extract_regex)]
    for patt, func in patterns_n_functions:
        result = func(patt, texto)
        if result:
            if type(result) == list:
                retorno = result[0].replace(".", "")
                return int(retorno)
            else:
                return int(result.replace(".", ""))


@click.command()
@common_options
def extraction_loop(clear, verbose):
    create_directory("json", clear)
    dicionario = dict_files("./txt/*.txt")
    for caminho, conteudo in dicionario.items():
        confirmados = get_confirmados(conteudo)
        dict_testes = get_testes(conteudo)
        aguardando = get_testes_aguardando(conteudo)
        obitos = get_obitos(conteudo)
        conteudo_json = {
            "casos_conf": confirmados,
            "obitos": obitos,
            "testes": dict_testes,
            "testes_aguardando": aguardando,
        }
        if "Internações" in conteudo:
            conteudo_json.update(
                {"leitos_SUS": get_leitos_sus(
                    conteudo), "UTI": get_uti_data(conteudo), }
            )
        json_path = caminho.replace("txt", "json", 2)
        if verbose:
            print(
                f"Encontrados dados em {caminho}. Extraindo para {json_path}")
        with open(json_path, "w") as fp:
            json.dump(conteudo_json, fp, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    extraction_loop()
