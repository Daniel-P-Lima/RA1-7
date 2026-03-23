import sys
import math
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
        else:
            resultado.append(caractere)

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
    linha = tratar_parenteses(linha)
    contexto = ContextoLexer(linha=linha)
    tokens = []

    estado_atual = estado_inicial

    while estado_atual is not None:
        estado_atual = estado_atual(contexto, tokens)

    return tokens

def converter_numero(valor: str) -> float:
    return float(valor)

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
        return float(math.trunc(esquerdo / direito))
    if operador == "%":
        return math.fmod(esquerdo, direito)
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

def lerArquivo(nome_arquivo: str, linhas: list) -> None:
    """
    Lê o arquivo de entrada, preenchendo a lista com as expressões não-vazias.
    Levanta FileNotFoundError com mensagem clara se o arquivo não existir.
    """
    try:
        with open(nome_arquivo, "r") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if linha:
                    linhas.append(linha)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {nome_arquivo}")
    except PermissionError:
        raise PermissionError(f"Sem permissão para ler o arquivo: {nome_arquivo}")
    except OSError as e:
        raise OSError(f"Erro ao abrir o arquivo: {e}")


def gerarAssembly(tokens: list[Token], codigo_assembly: list[str],
                  indice_linha: int, secao_dados: list[str],
                  memorias_labels: dict, resultados_labels: list) -> None:
    """
    Gera instruções ARMv7 para uma expressão RPN representada por tokens.
    Modifica codigo_assembly e secao_dados in-place.

    Estratégia: alocação estática de registradores VFP (d0-d15) como pilha
    de compilação — equivalente ao std::stack<float> do avaliador em C++.
    """
    sp = -1          # ponteiro virtual da pilha (índice do registrador d)
    const_idx = [0]  # contador de constantes para gerar labels únicos
    pow_idx = [0]    # contador de labels para loops de potenciação

    def add_constante(valor: float) -> str:
        label = f"_c{indice_linha}_{const_idx[0]}"
        const_idx[0] += 1
        secao_dados.append(f".align 8")
        secao_dados.append(f"{label}: .double {valor:.17g}")
        return label

    tokens_efetivos = [t for t in tokens if t.tipo != "PARENTESE"]
    codigo_assembly.append(f"    @ --- Linha {indice_linha} ---")

    for i, token in enumerate(tokens_efetivos):
        if token.tipo == "NUMERO":
            sp += 1
            label = add_constante(float(token.valor))
            codigo_assembly.append(f"    LDR r0, ={label}")
            codigo_assembly.append(f"    VLDR d{sp}, [r0]")

        elif token.tipo == "OPERADOR":
            rhs = sp
            lhs = sp - 1
            sp -= 1
            op = token.valor

            if op == "+":
                codigo_assembly.append(f"    VADD.F64 d{lhs}, d{lhs}, d{rhs}")
            elif op == "-":
                codigo_assembly.append(f"    VSUB.F64 d{lhs}, d{lhs}, d{rhs}")
            elif op == "*":
                codigo_assembly.append(f"    VMUL.F64 d{lhs}, d{lhs}, d{rhs}")
            elif op == "/":
                codigo_assembly.append(f"    VDIV.F64 d{lhs}, d{lhs}, d{rhs}")
            elif op == "//":
                # Divisão inteira com truncamento em direção a zero (comportamento C++)
                codigo_assembly.extend([
                    f"    VCVT.S32.F64 s0, d{lhs}",
                    f"    VCVT.S32.F64 s2, d{rhs}",
                    f"    VMOV r0, s0",
                    f"    VMOV r1, s2",
                    f"    SDIV r0, r0, r1",
                    f"    VMOV s0, r0",
                    f"    VCVT.F64.S32 d{lhs}, s0",
                ])
            elif op == "%":
                # Resto com sinal do dividendo (comportamento C++)
                codigo_assembly.extend([
                    f"    VCVT.S32.F64 s0, d{lhs}",
                    f"    VCVT.S32.F64 s2, d{rhs}",
                    f"    VMOV r0, s0",
                    f"    VMOV r1, s2",
                    f"    SDIV r2, r0, r1",
                    f"    MUL r2, r2, r1",
                    f"    SUB r0, r0, r2",
                    f"    VMOV s0, r0",
                    f"    VCVT.F64.S32 d{lhs}, s0",
                ])
            elif op == "^":
                # Potenciação via loop (assume expoente inteiro >= 0)
                label_1 = add_constante(1.0)
                lbl_loop = f"_pow_loop_{indice_linha}_{pow_idx[0]}"
                lbl_done = f"_pow_done_{indice_linha}_{pow_idx[0]}"
                pow_idx[0] += 1
                codigo_assembly.extend([
                    f"    @ Potenciacao: d{lhs} ^ d{rhs}",
                    f"    VCVT.S32.F64 s4, d{rhs}",
                    f"    VMOV r2, s4",
                    f"    LDR r0, ={label_1}",
                    f"    VLDR d{rhs}, [r0]",
                    f"{lbl_loop}:",
                    f"    CMP r2, #0",
                    f"    BEQ {lbl_done}",
                    f"    VMUL.F64 d{rhs}, d{rhs}, d{lhs}",
                    f"    SUB r2, r2, #1",
                    f"    B {lbl_loop}",
                    f"{lbl_done}:",
                    f"    VMOV.F64 d{lhs}, d{rhs}",
                ])

        elif token.tipo == "MEMORIA":
            nome = token.valor
            eh_ultimo = i == len(tokens_efetivos) - 1

            if nome not in memorias_labels:
                label = f"_mem_{nome}"
                memorias_labels[nome] = label
                secao_dados.append(f".align 8")
                secao_dados.append(f"{label}: .double 0.0")

            label = memorias_labels[nome]

            if eh_ultimo and sp >= 0:
                # Salvar em memória: (V MEM)
                codigo_assembly.append(f"    @ Salvar em {nome}")
                codigo_assembly.append(f"    LDR r0, ={label}")
                codigo_assembly.append(f"    VSTR d{sp}, [r0]")
            else:
                # Carregar da memória: (MEM)
                sp += 1
                codigo_assembly.append(f"    @ Carregar {nome}")
                codigo_assembly.append(f"    LDR r0, ={label}")
                codigo_assembly.append(f"    VLDR d{sp}, [r0]")

        elif token.tipo == "KEYWORD_RES":
            # N já foi empilhado pelo NUMERO anterior; substituímos pelo resultado histórico
            n = int(float(tokens_efetivos[i - 1].valor))
            idx_alvo = len(resultados_labels) - n
            if 0 <= idx_alvo < len(resultados_labels):
                label_res = resultados_labels[idx_alvo]
                codigo_assembly.append(f"    @ RES {n}: resultado da linha {idx_alvo + 1}")
                codigo_assembly.append(f"    LDR r0, ={label_res}")
                codigo_assembly.append(f"    VLDR d{sp}, [r0]")
            else:
                codigo_assembly.append(f"    @ ERRO: RES {n} fora do intervalo")

    # Armazenar resultado da linha para uso futuro por RES
    result_label = f"_result_{indice_linha}"
    secao_dados.append(f".align 8")
    secao_dados.append(f"{result_label}: .space 8")
    resultados_labels.append(result_label)
    if sp >= 0:
        codigo_assembly.append(f"    LDR r0, ={result_label}")
        codigo_assembly.append(f"    VSTR d{sp}, [r0]")
    codigo_assembly.append("")


def gerar_arquivo_assembly(expressoes: list[str]) -> str:
    """
    Gera um arquivo Assembly ARMv7 completo a partir de uma lista de expressões RPN.
    Retorna o conteúdo do arquivo como string.
    """
    codigo_assembly = []
    secao_dados = []
    memorias_labels = {}
    resultados_labels = []

    codigo_assembly.append(".global _start")
    codigo_assembly.append("")
    codigo_assembly.append("_start:")

    for i, expressao in enumerate(expressoes, start=1):
        try:
            tokens = parseExpressao(expressao)
            gerarAssembly(
                tokens=tokens,
                codigo_assembly=codigo_assembly,
                indice_linha=i,
                secao_dados=secao_dados,
                memorias_labels=memorias_labels,
                resultados_labels=resultados_labels,
            )
        except ValueError as e:
            codigo_assembly.append(f"    @ ERRO na linha {i}: {e}")
            resultados_labels.append(None)

    codigo_assembly.append("_halt:")
    codigo_assembly.append("    B _halt")
    codigo_assembly.append("")
    codigo_assembly.append(".data")
    codigo_assembly.extend(secao_dados)

    return "\n".join(codigo_assembly)


def main():
    if len(sys.argv) < 2:
        print("Uso: python programa.py <arquivo.txt>")
        print("     python programa.py <arquivo.txt> --assembly [saida.s]")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]
    gerar_asm = "--assembly" in sys.argv
    saida_asm = next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--assembly" and i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--")), "saida.s")

    linhas = []
    try:
        lerArquivo(caminho_arquivo, linhas)
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"Erro: {e}")
        sys.exit(1)

    if gerar_asm:
        assembly = gerar_arquivo_assembly(linhas)
        with open(saida_asm, "w") as f:
            f.write(assembly)
        print(f"Assembly gerado em: {saida_asm}")
        return

    estado_programa = EstadoPrograma()

    for i, expressao in enumerate(linhas, start=1):
        try:
            resultado = executarExpressao(expressao, estado_programa)
            estado_programa.historico_resultados.append(resultado)
            print(f"Linha {i}: {resultado}")
        except ValueError as erro:
            estado_programa.historico_resultados.append(None)
            print(f"Linha {i}: ERRO -> {erro}")

if __name__ == "__main__":
    main()
