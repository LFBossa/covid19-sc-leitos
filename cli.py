import functools

import click


def common_options(function):
    options = [
        click.option(
            "-c", "--clear", is_flag=True, help="Limpa diretório criado anteriormente",
        ),
        click.option(
            "-v",
            "--verbose",
            is_flag=True,
            help="Exibe mensagem com progresso do script",
        ),
    ]

    return functools.reduce(lambda f, opt: opt(f), options, function)
