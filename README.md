# COVID19 SC Leitos

Sistema que baixa os pdfs do site www.coronavirus.sc.gov.br, e le os dados para extrair informações. Gera o `dados-consolidados.csv`

## Dependências

Usando o `pipenv`
- `$ pipenv install` instalará as dependências necessárias contidas no `Pipfile`


Usando o `pip`
- `$ pip install -r requirements.txt`


*Obs*: É necessário ter o `pdftotext` no sistema

## Modo de usar

A maneira mais fácil é invocar o `$ pipenv shell` e após isso executar o arquivo `run.sh`


## Apoio

- [LABMAC - UFSC Blumenau](https://labmac.mat.blumenau.ufsc.br/)

## TODO

- Incorporar as informações das imagens e usar `tesseract` para OCR.