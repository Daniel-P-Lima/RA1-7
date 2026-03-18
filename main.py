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
    tem_ponto: bool = False

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
        contexto.tem_ponto = False
        return estado_numero

    if caractere.isalpha():
        contexto.lexema = ""
        return estado_identificador
    
    if caractere in "()":
        tokens.append(Token("PARENTESES", caractere))
        contexto.posicao += 1
        return estado_inicial

    if caractere in "+-*/%^":
        return estado_operador

    raise ValueError (
        f"Caractere inválido {caractere} na posição {contexto.posicao}"
    )

def estado_numero(contexto: ContextoLexer, tokens: list[Token]):
    while contexto.posicao < len(contexto.linha):
        caractere = contexto.linha[contexto.posicao]
        
        if caractere.isdigit():
            contexto.lexema += caractere
            contexto.posicao += 1
        elif caractere == ".":
            if contexto.tem_ponto:
                raise ValueError(
                    f"Número inválido: mais de um ponto decimal na posição {contexto.posicao}"
                )
            contexto.tem_ponto = True
            contexto.lexema += caractere
            contexto.posicao += 1
        else:
            break

    if contexto.lexema.endswith("."):
        raise ValueError(
            f"Número inválido terminado em ponto: '{contexto.lexema}'"
        )

    tokens.append(Token("NUMERO", contexto.lexema))
    contexto.lexema = ""
    contexto.tem_ponto = False
    return estado_inicial


def estado_operador(contexto: ContextoLexer, tokens: list[Token]):
    caractere = contexto.linha[contexto.posicao]

    if caractere == "/":
        proxima_posicao = contexto.posicao + 1

        if (
            proxima_posicao < len(contexto.linha)
            and contexto.linha[proxima_posicao] == "/"
        ):
            tokens.append(Token("OPERADOR", "//"))
            contexto.posicao += 2
            return estado_inicial

    tokens.append(Token("OPERADOR", caractere))
    contexto.posicao += 1
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

def converter_numero(valor: str):
    if "." in valor:
        return float(valor)
    return int(valor)

def aplicar_operador(operador: str, esquerdo, direito):
    if operador == "+":
        return esquerdo + direito
    if operador == "-":
        return esquerdo - direito
    if operador == "*":
        return esquerdo * direito
    if operador == "/":
        return esquerdo / direito
    if operador == "//":
        return esquerdo // direito
    if operador == "%":
        return esquerdo % direito
    if operador == "^":
        return esquerdo ** direito

    raise ValueError(f"Operador inválido: {operador}")

def avaliar_rpn(tokens: list[Token]):
    pilha = []

    for token in tokens:
        if token.tipo == "NUMERO":
            pilha.append(converter_numero(token.valor))

        elif token.tipo == "OPERADOR":
            if len(pilha) < 2:
                raise ValueError(
                    f"Expressão RPN inválida: operador '{token.valor}' sem operandos suficientes"
                )

            direito = pilha.pop()
            esquerdo = pilha.pop()

            if token.valor in {"/", "//", "%"} and direito == 0:
                raise ValueError("Divisão por zero")

            resultado = aplicar_operador(token.valor, esquerdo, direito)
            pilha.append(resultado)

        elif token.tipo == "IDENTIFICADOR":
            raise ValueError(
                f"Identificador '{token.valor}' ainda não é suportado nesta etapa"
            )

        elif token.tipo == "PARENTESE":
            raise ValueError(
                f"Parêntese '{token.valor}' não é válido em expressão RPN aritmética"
            )

        else:
            raise ValueError(f"Tipo de token desconhecido: {token.tipo}")

    if len(pilha) != 1:
        raise ValueError(
            f"Expressão RPN inválida: sobraram {len(pilha)} valores na pilha"
        )

    return pilha[0]

def main():
    caminho_arquivo = sys.argv[1]

    try:
        expressoes = ler_expressoes(caminho_arquivo)
        for i, expressao in enumerate(expressoes, start=1):
            tokens = analisar_lexicamente(expressao)
            resultado = avaliar_rpn(tokens)

            print(f"Linha {i}: {resultado} \n")

    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {caminho_arquivo}")
        sys.exit(1)


if __name__ == "__main__":
    main()


