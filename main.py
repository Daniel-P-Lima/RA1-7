# Instituicao: PUCPR - Pontificia Universidade Catolica do Parana
# Disciplina: Construcao de Interpretadores
# Professor: Frank Alcantara
# Grupo: RA1-7
# Integrantes:
#   Daniel Pereira Lima - GitHub: Daniel-P-Lima

import sys
import math
import io
import json
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
        historico_resultados=estado_programa.historico_resultados,    )
    estado_programa.memorias = memorias_temporarias
    return resultado

def lerArquivo(nome_arquivo: str, linhas: list) -> None:
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


def gerarAssembly(tokens: list[Token], codigo_assembly: list[str], indice_linha: int, secao_dados: list[str], memorias_labels: dict, resultados_labels: list) -> None:
    sp = -1          # ponteiro virtual da pilha (índice do registrador d)
    const_idx = [0]  # contador de constantes para gerar labels únicos
    pow_idx = [0]    # contador de labels para loops de potenciação

    def add_constante(valor: float) -> str:
        label = f"_c{indice_linha}_{const_idx[0]}"
        const_idx[0] += 1
        secao_dados.append(".align 8")
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

            if lhs < 0:
                codigo_assembly.append(f"    @ ERRO: operador '{op}' sem operandos suficientes (linha {indice_linha})")
                continue

            if op == "+":
                codigo_assembly.append(f"    VADD.F64 d{lhs}, d{lhs}, d{rhs}")
            elif op == "-":
                codigo_assembly.append(f"    VSUB.F64 d{lhs}, d{lhs}, d{rhs}")
            elif op == "*":
                codigo_assembly.append(f"    VMUL.F64 d{lhs}, d{lhs}, d{rhs}")
            elif op == "/":
                codigo_assembly.append(f"    VDIV.F64 d{lhs}, d{lhs}, d{rhs}")
            elif op == "//":
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
                secao_dados.append(".align 8")
                secao_dados.append(f"{label}: .double 0.0")

            label = memorias_labels[nome]

            if eh_ultimo and sp >= 0:
                codigo_assembly.append(f"    @ Salvar em {nome}")
                codigo_assembly.append(f"    LDR r0, ={label}")
                codigo_assembly.append(f"    VSTR d{sp}, [r0]")
            else:
                sp += 1
                codigo_assembly.append(f"    @ Carregar {nome}")
                codigo_assembly.append(f"    LDR r0, ={label}")
                codigo_assembly.append(f"    VLDR d{sp}, [r0]")

        elif token.tipo == "KEYWORD_RES":
            n = int(float(tokens_efetivos[i - 1].valor))
            idx_alvo = len(resultados_labels) - n
            if 0 <= idx_alvo < len(resultados_labels):
                label_res = resultados_labels[idx_alvo]
                codigo_assembly.append(f"    @ RES {n}: resultado da linha {idx_alvo + 1}")
                codigo_assembly.append(f"    LDR r0, ={label_res}")
                codigo_assembly.append(f"    VLDR d{sp}, [r0]")
            else:
                codigo_assembly.append(f"    @ ERRO: RES {n} fora do intervalo")

    result_label = f"_result_{indice_linha}"
    secao_dados.append(".align 8")
    secao_dados.append(f"{result_label}: .space 8")
    resultados_labels.append(result_label)
    if sp >= 0:
        codigo_assembly.append(f"    LDR r0, ={result_label}")
        codigo_assembly.append(f"    VSTR d{sp}, [r0]")
        codigo_assembly.append(f"    VCVT.S32.F64 s0, d{sp}    @ truncar resultado para inteiro")
        codigo_assembly.append(f"    VMOV r1, s0")
        codigo_assembly.append(f"    BL _show_hex")
    codigo_assembly.append("")


def gerar_arquivo_assembly(expressoes: list[str]) -> str:
    codigo_assembly = []
    secao_dados = []
    memorias_labels = {}
    resultados_labels = []

    codigo_assembly.append(".arch_extension idiv   @ habilita SDIV em ARM mode (Cortex-A9)")
    codigo_assembly.append(".global _start")
    codigo_assembly.append("")
    codigo_assembly.append("_start:")
    codigo_assembly.append("    LDR sp, =0x3FFFFFFC    @ inicializar pilha (fim da SDRAM)")

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
    codigo_assembly.append("@ Subrotina: exibe inteiro com sinal em HEX0-3 e LEDR")
    codigo_assembly.append("@ Entrada: r1 = valor inteiro com sinal (parte inteira do resultado)")
    codigo_assembly.append("@ HEX mostra parte inteira; LEDR mostra bits brutos")
    codigo_assembly.append("_show_hex:")
    codigo_assembly.append("    PUSH {r2, r3, r4, r5, r6, lr}")
    codigo_assembly.append("    LDR r0, =0xFF200000        @ LEDR")
    codigo_assembly.append("    STR r1, [r0]")
    codigo_assembly.append("    LDR r0, =0xFF200030        @ HEX4-5")
    codigo_assembly.append("    CMP r1, #0")
    codigo_assembly.append("    BPL _show_hex_pos")
    codigo_assembly.append("    MOV r2, #0x40              @ sinal de menos no HEX5")
    codigo_assembly.append("    LSL r2, r2, #8")
    codigo_assembly.append("    STR r2, [r0]")
    codigo_assembly.append("    NEG r1, r1")
    codigo_assembly.append("    B _show_hex_digits")
    codigo_assembly.append("_show_hex_pos:")
    codigo_assembly.append("    MOV r2, #0")
    codigo_assembly.append("    STR r2, [r0]               @ apaga HEX4-5")
    codigo_assembly.append("_show_hex_digits:")
    codigo_assembly.append("    LDR r5, =_seg7_table")
    codigo_assembly.append("    MOV r6, #0                 @ palavra acumuladora dos segmentos")
    codigo_assembly.append("    MOV r2, #10")
    codigo_assembly.append("    @ HEX0: digito das unidades")
    codigo_assembly.append("    SDIV r3, r1, r2")
    codigo_assembly.append("    MUL r4, r3, r2")
    codigo_assembly.append("    SUB r4, r1, r4")
    codigo_assembly.append("    LDRB r4, [r5, r4]")
    codigo_assembly.append("    ORR r6, r6, r4")
    codigo_assembly.append("    MOV r1, r3")
    codigo_assembly.append("    @ HEX1: digito das dezenas")
    codigo_assembly.append("    SDIV r3, r1, r2")
    codigo_assembly.append("    MUL r4, r3, r2")
    codigo_assembly.append("    SUB r4, r1, r4")
    codigo_assembly.append("    LDRB r4, [r5, r4]")
    codigo_assembly.append("    LSL r4, r4, #8")
    codigo_assembly.append("    ORR r6, r6, r4")
    codigo_assembly.append("    MOV r1, r3")
    codigo_assembly.append("    @ HEX2: digito das centenas")
    codigo_assembly.append("    SDIV r3, r1, r2")
    codigo_assembly.append("    MUL r4, r3, r2")
    codigo_assembly.append("    SUB r4, r1, r4")
    codigo_assembly.append("    LDRB r4, [r5, r4]")
    codigo_assembly.append("    LSL r4, r4, #16")
    codigo_assembly.append("    ORR r6, r6, r4")
    codigo_assembly.append("    MOV r1, r3")
    codigo_assembly.append("    @ HEX3: digito das centenas")
    codigo_assembly.append("    SDIV r3, r1, r2")
    codigo_assembly.append("    MUL r4, r3, r2")
    codigo_assembly.append("    SUB r4, r1, r4")
    codigo_assembly.append("    LDRB r4, [r5, r4]")
    codigo_assembly.append("    LSL r4, r4, #24")
    codigo_assembly.append("    ORR r6, r6, r4")
    codigo_assembly.append("    @ Supressao de zeros a esquerda")
    codigo_assembly.append("    @ Se HEX3 == segmento '0' (0x3F), apaga")
    codigo_assembly.append("    LSR r3, r6, #24")
    codigo_assembly.append("    CMP r3, #0x3F")
    codigo_assembly.append("    BNE _no_blank_hex3")
    codigo_assembly.append("    BIC r6, r6, #0xFF000000")
    codigo_assembly.append("_no_blank_hex3:")
    codigo_assembly.append("    @ Se HEX3 apagado E HEX2 == '0', apaga HEX2 tambem")
    codigo_assembly.append("    TST r6, #0xFF000000")
    codigo_assembly.append("    BNE _no_blank_hex2")
    codigo_assembly.append("    LSR r3, r6, #16")
    codigo_assembly.append("    AND r3, r3, #0xFF")
    codigo_assembly.append("    CMP r3, #0x3F")
    codigo_assembly.append("    BNE _no_blank_hex2")
    codigo_assembly.append("    BIC r6, r6, #0x00FF0000")
    codigo_assembly.append("_no_blank_hex2:")
    codigo_assembly.append("    LDR r0, =0xFF200020        @ HEX0-3")
    codigo_assembly.append("    STR r6, [r0]")
    codigo_assembly.append("    POP {r2, r3, r4, r5, r6, pc}")
    codigo_assembly.append("")
    codigo_assembly.append(".data")
    codigo_assembly.append("_seg7_table:")
    codigo_assembly.append("    .byte 0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F")
    codigo_assembly.extend(secao_dados)

    return "\n".join(codigo_assembly)

def salvar_tokens(tokens_por_linha: list[list[Token]], caminho_saida: str = "tokens.json") -> None:
    """
    Salva os tokens gerados pelo analisador léxico em arquivo JSON.
    Apenas os tokens da última execução são mantidos (arquivo sobrescrito).
    Formato: lista de objetos {linha, tokens: [{tipo, valor}, ...]}
    """
    dados = [
        {
            "linha": i + 1,
            "tokens": [{"tipo": t.tipo, "valor": t.valor} for t in tokens]
        }
        for i, tokens in enumerate(tokens_por_linha)
    ]
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def formatar_resultado(valor: Union[float, None]) -> str:
    if valor is None:
        return "ERRO"
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return f"{valor:.1f}"

def exibirResultados(resultados: list[Union[float, None]], erros: dict = None) -> None:
    if erros is None:
        erros = {}
    for i, resultado in enumerate(resultados, start=1):
        if resultado is None and i in erros:
            print(f"Linha {i}: ERRO -> {erros[i]}")
        else:
            print(f"Linha {i}: {formatar_resultado(resultado)}")

def executar_testes():
    total = 0
    passou = 0

    def checar(descricao: str, resultado, esperado):
        nonlocal total, passou
        total += 1
        ok = resultado == esperado
        if ok:
            passou += 1
        status = "OK" if ok else f"FALHOU (esperado={esperado!r}, obtido={resultado!r})"
        print(f"  [{status}] {descricao}")

    def checar_erro(descricao: str, expressao: str, estado=None):
        nonlocal total, passou
        total += 1
        if estado is None:
            estado = EstadoPrograma()
        try:
            executarExpressao(expressao, estado)
            print(f"  [FALHOU] {descricao} — esperava erro, mas não ocorreu")
        except (ValueError, Exception):
            passou += 1
            print(f"  [OK] {descricao}")

    # --- AFD ---
    print("\n=== Testes do AFD (Analisador Léxico) ===")

    tokens = parseExpressao("3.14 2.0 +")
    checar("'3.14 2.0 +' gera 3 tokens", len(tokens), 3)
    checar("token[0] = NUMERO '3.14'", (tokens[0].tipo, tokens[0].valor), ("NUMERO", "3.14"))
    checar("token[1] = NUMERO '2.0'",  (tokens[1].tipo, tokens[1].valor), ("NUMERO", "2.0"))
    checar("token[2] = OPERADOR '+'",  (tokens[2].tipo, tokens[2].valor), ("OPERADOR", "+"))

    tokens = parseExpressao("5 RES")
    checar("'5 RES' gera 2 tokens", len(tokens), 2)
    checar("token[0] = NUMERO '5'",   (tokens[0].tipo, tokens[0].valor), ("NUMERO", "5"))
    checar("token[1] = KEYWORD_RES",  tokens[1].tipo, "KEYWORD_RES")

    checar_erro("'3.14.5 2.0 +' é inválido (duplo ponto)", "3.14.5 2.0 +")

    tokens = parseExpressao("( 3 2 + )")
    tipos = [t.tipo for t in tokens]
    checar("Parêntese aninhado: abertura reconhecida", tipos[0], "PARENTESE")
    checar("Parêntese aninhado: fechamento reconhecido", tipos[-1], "PARENTESE")

    checar_erro("Parêntese sem fechamento '( 3 2 +'", "( 3 2 +")
    checar_erro("Parêntese sem abertura '3 2 + )'",   "3 2 + )")

    # --- executarExpressao ---
    print("\n=== Testes de executarExpressao ===")

    estado = EstadoPrograma()
    checar("3 4 + = 7",       executarExpressao("3 4 +",   estado), 7.0)
    checar("10 3 - = 7",      executarExpressao("10 3 -",  estado), 7.0)
    checar("6 7 * = 42",      executarExpressao("6 7 *",   estado), 42.0)
    checar("10 4 / = 2.5",    executarExpressao("10 4 /",  estado), 2.5)
    checar("10 3 // = 3",     executarExpressao("10 3 //", estado), 3.0)
    checar("10 3 % = 1",      executarExpressao("10 3 %",  estado), 1.0)
    checar("2 8 ^ = 256",     executarExpressao("2 8 ^",   estado), 256.0)
    checar("-5 3 + = -2",     executarExpressao("-5 3 +",  estado), -2.0)
    checar(".5 .5 + = 1.0",   executarExpressao(".5 .5 +", estado), 1.0)

    checar_erro("Divisão por zero '5 0 /'",               "5 0 /")
    checar_erro("Operador sem operandos suficientes '+'",  "+")

    # --- Memória (V MEM) e (MEM) ---
    print("\n=== Testes de Memória — FSM com comandos especiais ===")

    estado = EstadoPrograma()
    executarExpressao("42 MEM", estado)
    checar("(V MEM): 42 armazenado em MEM",   estado.memorias.get("MEM"), 42.0)
    checar("(MEM): recuperar MEM = 42",        executarExpressao("MEM 0 +", estado), 42.0)

    estado = EstadoPrograma()
    executarExpressao("10 A", estado)
    executarExpressao("20 B", estado)
    checar("Múltiplas variáveis: A = 10",  estado.memorias.get("A"), 10.0)
    checar("Múltiplas variáveis: B = 20",  estado.memorias.get("B"), 20.0)
    checar("A B + = 30",                   executarExpressao("A B +", estado), 30.0)

    estado = EstadoPrograma()
    executarExpressao("5 X", estado)
    executarExpressao("10 X", estado)
    checar("Sobreescrever X com 10", estado.memorias.get("X"), 10.0)

    # --- Histórico RES ---
    print("\n=== Testes de Histórico (RES) ===")

    estado = EstadoPrograma()
    estado.historico_resultados.extend([10.0, 20.0])
    checar("1 RES = 20 (último)",     executarExpressao("1 RES", estado), 20.0)
    checar("2 RES = 10 (penúltimo)",  executarExpressao("2 RES", estado), 10.0)

    checar_erro("RES sem linhas anteriores", "1 RES", EstadoPrograma())
    checar_erro("0 RES é inválido",          "0 RES")

    estado = EstadoPrograma()
    estado.historico_resultados.append(None)
    checar_erro("RES aponta para linha com erro (None)", "1 RES", estado)

    # --- formatar_resultado e exibirResultados ---
    print("\n=== Testes de exibirResultados ===")

    checar("formatar inteiro 7.0  → '7'",   formatar_resultado(7.0),   "7")
    checar("formatar real 3.14    → '3.1'", formatar_resultado(3.14),  "3.1")
    checar("formatar None         → 'ERRO'",formatar_resultado(None),  "ERRO")
    checar("formatar 256.0        → '256'", formatar_resultado(256.0), "256")
    checar("formatar 2.5          → '2.5'", formatar_resultado(2.5),   "2.5")

    captura = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = captura
    exibirResultados([7.0, 3.14, None, 256.0], erros={3: "Divisão por zero"})
    sys.stdout = sys_stdout
    saida = captura.getvalue().strip().split("\n")
    checar("exibirResultados linha 1 = 'Linha 1: 7'",                    saida[0], "Linha 1: 7")
    checar("exibirResultados linha 2 = 'Linha 2: 3.1'",                  saida[1], "Linha 2: 3.1")
    checar("exibirResultados linha 3 = 'Linha 3: ERRO -> Divisão por zero'", saida[2], "Linha 3: ERRO -> Divisão por zero")
    checar("exibirResultados linha 4 = 'Linha 4: 256'",                  saida[3], "Linha 4: 256")

    # --- Programa completo (lerArquivo → executarExpressao → exibirResultados) ---
    print("\n=== Teste do programa completo (10 linhas) ===")

    import tempfile, os
    expressoes_teste = [
        "3.14 2.0 +",           # 5.14  → 5.1
        "5.0 MEM",              # salva 5.0; resultado 5.0 → 5
        "MEM 2.0 *",            # 5 * 2 = 10 → 10
        "10 3 //",              # 3 → 3
        "10 3 %",               # 1 → 1
        "2 8 ^",                # 256 → 256
        "1 RES",                # result da linha 6 = 256 → 256
        "1.5 2.0 * 3.0 4.0 *",  # 3.0 12.0 (2 valores na pilha — ERRO)
        "-5 3 +",               # -2 → -2
        ".5 .5 +",              # 1.0 → 1
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("\n".join(expressoes_teste))
        nome_tmp = f.name

    try:
        linhas = []
        lerArquivo(nome_tmp, linhas)
        checar("lerArquivo lê 10 linhas", len(linhas), 10)

        estado = EstadoPrograma()
        resultados = []
        erros_prog = {}
        for i, expr in enumerate(linhas, start=1):
            try:
                r = executarExpressao(expr, estado)
                estado.historico_resultados.append(r)
                resultados.append(r)
            except ValueError as e:
                estado.historico_resultados.append(None)
                resultados.append(None)
                erros_prog[i] = str(e)

        checar("10 resultados coletados",          len(resultados), 10)
        checar("linha 1 = 5.14",                   resultados[0], 5.140000000000001)
        checar("linha 2 = 5.0 (V MEM)",            resultados[1], 5.0)
        checar("linha 3 = 10.0 (MEM * 2)",         resultados[2], 10.0)
        checar("linha 4 = 3.0 (10 // 3)",          resultados[3], 3.0)
        checar("linha 5 = 1.0 (10 % 3)",           resultados[4], 1.0)
        checar("linha 6 = 256.0 (2 ^ 8)",          resultados[5], 256.0)
        checar("linha 7 = 256.0 (1 RES)",          resultados[6], 256.0)
        checar("linha 8 = None (pilha inválida)",   resultados[7], None)
        checar("linha 9 = -2.0 (-5 + 3)",          resultados[8], -2.0)
        checar("linha 10 = 1.0 (.5 + .5)",         resultados[9], 1.0)

    finally:
        os.unlink(nome_tmp)

    total += 1
    try:
        lerArquivo("__arquivo_inexistente__.txt", [])
        print("  [FALHOU] lerArquivo arquivo inexistente — não levantou erro")
    except FileNotFoundError:
        passou += 1
        print("  [OK] lerArquivo arquivo inexistente levanta FileNotFoundError")

    print(f"\n=== Resultado: {passou}/{total} testes passaram ===\n")

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--testes":
        executar_testes()
        return
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
    resultados = []
    erros = {}
    tokens_por_linha = []

    for i, expressao in enumerate(linhas, start=1):
        try:
            tokens = parseExpressao(expressao)
            tokens_por_linha.append(tokens)
            resultado = executarExpressao(expressao, estado_programa)
            estado_programa.historico_resultados.append(resultado)
            resultados.append(resultado)
        except ValueError as erro:
            tokens_por_linha.append([])
            estado_programa.historico_resultados.append(None)
            resultados.append(None)
            erros[i] = str(erro)

    salvar_tokens(tokens_por_linha)
    exibirResultados(resultados, erros)

if __name__ == "__main__":
    main()
