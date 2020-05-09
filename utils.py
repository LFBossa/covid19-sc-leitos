import os
import shutil


def create_directory(path, clear):
    if clear:
        print(f"Limpando o diretório ./{path}/")
        shutil.rmtree(f"./{path}/")
    os.makedirs(path, exist_ok=True)
