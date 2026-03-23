import sys
from dataclasses import dataclass, field
from typing import Union


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
    quantidade_digitos: int = 0

@dataclass
class EstadoPrograma:
    memorias: dict[str, Union[int, float]] = field(default_factory=dict)
    historico_resultados: list[Union[int, float, None]] = field(default_factory=list)


def ler_expressoes(caminho_arquivo: str) -> list[str]:
    expressoes = []

    with open(caminho_arquivo, "r") as arquivo:
        for linha in arquivo:
            linha = linha.strip()

            if linha:
                expressoes.append(linha) # array de strings 

    return expressoes

def tratar_parenteses(linha: str) -> str:
    pilha_parenteses = []
    resultado = []

    for posicao, caractere in enumerate(linha):
        if caractere == "(":
            pilha_parenteses.append(posicao)
            resultado.append(" ( ")
        elif caractere == ")":
            if not pilha_parenteses:
                raise ValueError(f"Parêntese fechado sem abertura na posição {posicao}")
            pilha_parenteses.pop()
            resultado.append(" ) ")

    if pilha_parenteses:
        posicao_abertura = pilha_parenteses[-1]
        raise ValueError(
            f"Parêntese aberto sem fechamento na posição {posicao_abertura}"
        )

    linha_normalizada = "".join(resultado)
    linha_normalizada = " ".join(linha_normalizada.split())
    return linha_normalizada

def caractere_anterior_permite_sinal(contexto: ContextoLexer) -> bool:
    if contexto.posicao == 0:
        return True

    anterior = contexto.linha[contexto.posicao - 1]
    return anterior.isspace() or anterior == "("


def eh_inicio_decimal(contexto: ContextoLexer) -> bool:
    if contexto.linha[contexto.posicao] != ".":
        return False

    proxima_posicao = contexto.posicao + 1
    return (
        proxima_posicao < len(contexto.linha)
        and contexto.linha[proxima_posicao].isdigit()
    )


def eh_inicio_numero_negativo(contexto: ContextoLexer) -> bool:
    if contexto.linha[contexto.posicao] != "-":
        return False

    if not caractere_anterior_permite_sinal(contexto):
        return False

    proxima_posicao = contexto.posicao + 1
    if proxima_posicao >= len(contexto.linha):
        return False

    proximo = contexto.linha[proxima_posicao]

    if proximo.isdigit():
        return True

    if proximo == ".":
        proxima_proxima_posicao = contexto.posicao + 2
        return (
            proxima_proxima_posicao < len(contexto.linha)
            and contexto.linha[proxima_proxima_posicao].isdigit()
        )

    return False

def estado_inicial(contexto: ContextoLexer, tokens: list[Token]):
    while (contexto.posicao < len(contexto.linha) and contexto.linha[contexto.posicao].isspace()):
        contexto.posicao += 1

    if contexto.posicao >= len(contexto.linha):
        return None

    caractere = contexto.linha[contexto.posicao]

    if caractere.isdigit() or eh_inicio_decimal(contexto):
        contexto.lexema = ""
        contexto.tem_ponto = False
        return estado_numero
   
    if eh_inicio_numero_negativo(contexto):
        contexto.lexema = "-"
        contexto.tem_ponto = False
        contexto.quantidade_digitos = 0
        contexto.posicao += 1
        return estado_numero
   
    if caractere.isupper():
        contexto.lexema = ""
        return estado_identificador

    if caractere in "()":
        tokens.append(Token("PARENTESE", caractere))
        contexto.posicao += 1
        return estado_inicial

    if caractere in "+-*/%^":
        return estado_operador

    raise ValueError(f"Caractere inválido '{caractere}' na posição {contexto.posicao}")

def estado_numero(contexto: ContextoLexer, tokens: list[Token]):
    while contexto.posicao < len(contexto.linha):
        caractere = contexto.linha[contexto.posicao]

        if caractere.isdigit():
            contexto.lexema += caractere
            contexto.quantidade_digitos += 1
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

    if contexto.quantidade_digitos == 0:
        raise ValueError(f"Número inválido: '{contexto.lexema}'")

    if contexto.lexema.endswith("."):
        raise ValueError(
            f"Número inválido terminado em ponto: '{contexto.lexema}'"
        )

    tokens.append(Token("NUMERO", contexto.lexema))
    contexto.lexema = ""
    contexto.tem_ponto = False
    contexto.quantidade_digitos = 0
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


def estado_identificador(contexto: ContextoLexer, tokens: list[Token]):
    while (contexto.posicao < len(contexto.linha) and contexto.linha[contexto.posicao].isupper()):
        contexto.lexema += contexto.linha[contexto.posicao]
        contexto.posicao += 1

    if contexto.lexema == "RES":
        tokens.append(Token("KEYWORD_RES", contexto.lexema))
    else:
        tokens.append(Token("MEMORIA", contexto.lexema))

    contexto.lexema = ""
    return estado_inicial

def parseExpressao(linha: str) -> list[Token]:
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

def validar_indice_res(valor):
    if isinstance(valor, float):
        if not valor.is_integer():
            raise ValueError("RES exige um inteiro não negativo")
        valor = int(valor)

    if not isinstance(valor, int):
        raise ValueError("RES exige um inteiro não negativo")

    if valor < 0:
        raise ValueError("RES exige um inteiro não negativo")

    if valor == 0:
        raise ValueError("0 RES é inválido: a linha atual ainda não possui resultado")

    return valor


def resolver_res(n_linhas: int, historico_resultados: list[Union[int, float, None]]):
    if n_linhas > len(historico_resultados):
        raise ValueError(
            f"RES inválido: não existem {n_linhas} linhas anteriores"
        )

    indice_alvo = len(historico_resultados) - n_linhas
    resultado = historico_resultados[indice_alvo]

    if resultado is None:
        raise ValueError(
            f"RES inválido: a linha referenciada ({indice_alvo + 1}) não possui resultado válido"
        )

    return resultado


def avaliar_rpn(tokens: list[Token], memorias: dict[str, Union[int, float]], historico_resultados: list[Union[int, float, None]]):
    pilha = []

    for indice, token in enumerate(tokens):
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

        elif token.tipo == "KEYWORD_RES":
            if not pilha:
                raise ValueError("RES exige um valor N antes da keyword")

            n_linhas = validar_indice_res(pilha.pop())
            resultado_anterior = resolver_res(n_linhas, historico_resultados)
            pilha.append(resultado_anterior)

        elif token.tipo == "MEMORIA":
            nome_memoria = token.valor
            eh_ultimo_token = indice == len(tokens) - 1

            if eh_ultimo_token and pilha:
                memorias[nome_memoria] = pilha[-1]
            else:
                pilha.append(memorias.get(nome_memoria, 0.0))

        elif token.tipo == "PARENTESE":
            continue

        else:
            raise ValueError(f"Tipo de token desconhecido: {token.tipo}")

    if len(pilha) != 1:
        raise ValueError(
            f"Expressão RPN inválida: sobraram {len(pilha)} valores na pilha"
        )

    return pilha[0]


def executarExpressao(expressao: str, estado_programa: EstadoPrograma):
    tokens = parseExpressao(expressao)

    memorias_temporarias = estado_programa.memorias.copy()

    resultado = avaliar_rpn(
        tokens=tokens,
        memorias=memorias_temporarias,
        historico_resultados=estado_programa.historico_resultados,
    )

    estado_programa.memorias = memorias_temporarias
    return resultado

def main():
    if len(sys.argv) < 2:
        print("Uso: python programa.py <arquivo.txt>")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]

    try:
        expressoes = ler_expressoes(caminho_arquivo)
    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {caminho_arquivo}")
        sys.exit(1)

    estado_programa = EstadoPrograma()

    for i, expressao in enumerate(expressoes, start=1):
        try:
            resultado = executarExpressao(expressao, estado_programa)
            estado_programa.historico_resultados.append(resultado)
            print(f"Linha {i}: {resultado}")
        except ValueError as erro:
            estado_programa.historico_resultados.append(None)
            print(f"Linha {i}: ERRO -> {erro}")

if __name__ == "__main__":
    main()
