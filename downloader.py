import datetime as dt 
from urllib.request import urlretrieve

def get_link_from_isostring(data_isostring):
    URL = "https://www.coronavirus.sc.gov.br/wp-content/uploads/{ano}/{mes}/boletim-epidemiologico-{dia}-{mes}-{ano}.pdf"
    ano, mes, dia = data_isostring.split("-")
    return URL.format(ano=ano, mes=mes, dia=dia)

def download_loop():
    INICIO = dt.date(2020,4,14)
    numero_dias = (INICIO.today() - INICIO).days
    for n in range(numero_dias):
        dia = INICIO + dt.timedelta(n)
        dia_iso = dia.isoformat()
        link = get_link_from_isostring(dia_iso)
        print(f"Baixando o relatório do dia {dia.strftime('%d/%m/%y')}")
        urlretrieve(link, filename=dia_iso+".pdf")

if __name__ == "__main__":
    download_loop()