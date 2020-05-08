from PIL import Image
import pytesseract as ocr
from PyPDF2 import PdfFileReader
import io
from extract import ls


def extract_save_images(pdf_path):
    pdf = PdfFileReader(open(pdf_path, "rb"))
    data_iso = pdf_path.strip("/.pdf")
    # pegamos a pagina
    pagina = pdf.getPage(0)
    # pegamos os objetos
    xobjects = pagina["/Resources"]["/XObject"]
    # isso aqui foi descoberto na mão
    heuristica = {'Casos confirmados por sexo': 'sexo.confirmados',
                  'Obitos por sexo': 'sexo.obitos',
                  'Obitos por faixa etaria': 'histograma.obitos',
                  'Casos por faixa etaria': 'histograma.confirmados'}
    
    for key, val in xobjects.items():
        objeto = val.getObject()
        img = Image.open(io.BytesIO(objeto._data))
        txt = ocr.image_to_string(img)
        for tag in heuristica.keys():
            if tag in txt:
                print(key, "->", heuristica[tag])
                img.save(f"./jpeg/{data_iso}_{heuristica[tag]}.jpeg", "JPEG")
                continue

# Heurística
# /Image12 - Casos por faixa etária
# /Image13 - Confirmados por sexo
# /Image14 - Mortes por sexo
# /Image16 - Obitos por faixa etaria

def main_loop():
    for x in ls("./pdf/*.pdf"):
        
        print(x)
        extract_save_images(x)


if __name__ == "__main__":
    main_loop()
