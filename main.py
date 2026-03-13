import sys
from dataclasses import dataclass

@dataclass
class Token:
    tipo: str
    valor: str

@dataclass
class ContextoLexer:
    linha: str
    posicao: int = 0
    lexema: str = ""

def ler_expressoes(caminho_arquivo: str) -> list[str]:
    expressoes = []

    with open(caminho_arquivo, "r") as arquivo:
        for linha in arquivo:
            linha = linha.strip()

            if linha:
                expressoes.append(linha) # array de strings 

    return expressoes

def estado_inicial(contexto: ContextoLexer, tokens: list[Token]):
    while contexto.posicao < len(contexto.linha) and contexto.linha[contexto.posicao].isspace():
        contexto.posicao += 1

    if contexto.posicao >= len(contexto.linha):
        return None

    caractere = contexto.linha[contexto.posicao]

    if caractere.isdigit():
        contexto.lexema = ""
        return estado_numero

    if caractere.isalpha():
        contexto.lexema = ""
        return estado_identificador
    
    if caractere in "+-*/%^()":
        tokens.append(Token("OPERADOR", caractere))
        contexto.posicao += 1
        return estado_inicial
    
    raise ValueError (
        f"Caractere inválido {caractere} na posição {contexto.posicao}"
    )



def estado_numero(contexto: ContextoLexer, tokens: list[Token]):
    while contexto.posicao < len(contexto.linha) and contexto.linha[contexto.posicao].isdigit():
        contexto.lexema += contexto.linha[contexto.posicao]
        contexto.posicao += 1

    tokens.append(Token("NUMERO", contexto.lexema))
    contexto.lexema = ""
    return estado_inicial

def estado_identificador(ctx: ContextoLexer, tokens: list[Token]):
    while ctx.posicao < len(ctx.linha) and ctx.linha[ctx.posicao].isalpha():
        ctx.lexema += ctx.linha[ctx.posicao]
        ctx.posicao += 1

    tokens.append(Token("IDENTIFICADOR", ctx.lexema))
    ctx.lexema = ""
    return estado_inicial

def analisar_lexicamente(linha: str) -> list[Token]:
    contexto = ContextoLexer(linha=linha)
    tokens = []

    estado_atual = estado_inicial

    while estado_atual is not None:
        estado_atual = estado_atual(contexto, tokens)

    return tokens

def main():
    caminho_arquivo = sys.argv[1]

    try:
        expressoes = ler_expressoes(caminho_arquivo)
        for i, expressao in enumerate(expressoes, start=1):
            tokens = analisar_lexicamente(expressao)
            print(f"Linha {i}: {tokens}")

    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {caminho_arquivo}")
        sys.exit(1)


if __name__ == "__main__":
    main()


