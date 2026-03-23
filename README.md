# RA1-7 — Analisador Léxico e Gerador de Assembly ARMv7

**Grupo:** RA1-7
**Disciplina:** Construção de Interpretadores
**Integrantes:**
- Daniel Pereira Lima — GitHub: [Daniel-P-Lima](https://github.com/Daniel-P-Lima)

---

## Descrição

Analisador léxico de expressões matemáticas em **notação polonesa reversa (RPN)** com gerador de código **Assembly ARMv7** compatível com o simulador CPulator-ARMv7 DEC1-SOC (v16.1).

O programa lê um arquivo de texto com expressões RPN (uma por linha), tokeniza cada expressão usando um **Autômato Finito Determinístico (AFD)**, avalia os resultados e opcionalmente traduz o programa para Assembly ARMv7.

---

## Estrutura do Repositório

```
.
├── main.py          # Código-fonte principal (Python)
├── teste1.txt       # Arquivo de teste 1 — expressões mistas com erros
├── teste2.txt       # Arquivo de teste 2 — expressões com reais, // e MEM
├── teste3.txt       # Arquivo de teste 3 — testes de robustez e erros léxicos
├── teste1.s         # Assembly ARMv7 gerado na última execução de teste1.txt
├── tokens.json      # Tokens gerados na última execução do analisador léxico
└── README.md
```

---

## Requisitos

- Python 3.10 ou superior (usa `match`/`dataclass` moderno)
- Nenhuma dependência externa

---

## Como Executar

### Modo normal — avalia expressões e exibe resultados

```bash
python3 main.py <arquivo.txt>
```

Exemplo:

```bash
python3 main.py teste1.txt
```

Saída:

```
Linha 1: 7
Linha 2: ERRO -> Expressão RPN inválida: operador '/' sem operandos suficientes
Linha 3: 46.3
...
```

A cada execução, os tokens gerados pelo analisador léxico são salvos automaticamente em `tokens.json`.

---

### Modo Assembly — gera código ARMv7

```bash
python3 main.py <arquivo.txt> --assembly [saida.s]
```

Exemplo:

```bash
python3 main.py teste1.txt --assembly teste1.s
```

O arquivo `.s` gerado é compatível com o CPulator-ARMv7 DEC1-SOC (v16.1) e pode ser colado diretamente no simulador.

---

### Modo testes — executa a suíte de testes automáticos

```bash
python3 main.py --testes
```

Cobre: AFD, todos os operadores, memória (`MEM`), histórico (`RES`), `exibirResultados` e programa completo com 10 linhas.

---

## Sintaxe das Expressões RPN

Cada linha do arquivo de entrada contém uma expressão em notação polonesa reversa. Operandos e operadores são separados por espaços.

### Operadores suportados

| Operador | Descrição                        | Exemplo         | Resultado |
|----------|----------------------------------|-----------------|-----------|
| `+`      | Adição                           | `3 4 +`         | `7`       |
| `-`      | Subtração                        | `10 3 -`        | `7`       |
| `*`      | Multiplicação                    | `6 7 *`         | `42`      |
| `/`      | Divisão real                     | `10 4 /`        | `2.5`     |
| `//`     | Divisão inteira (trunca p/ zero) | `10 3 //`       | `3`       |
| `%`      | Resto (sinal do dividendo)       | `10 3 %`        | `1`       |
| `^`      | Potenciação (expoente inteiro)   | `2 8 ^`         | `256`     |

### Tipos de tokens

| Token         | Descrição                                | Exemplo        |
|---------------|------------------------------------------|----------------|
| Número real   | Ponto como separador decimal             | `3.14`, `.5`   |
| Número negativo | Sinal `-` seguido de dígito           | `-5`, `-.5`    |
| Parênteses    | Agrupamento visual (ignorado na avaliação) | `( 3 4 + )` |
| `N RES`       | Resultado de N linhas atrás              | `1 RES`        |
| `V MEM`       | Armazenar valor em variável              | `42 MEM`       |
| `MEM`         | Carregar valor da variável               | `MEM`          |

Variáveis são nomes em **letras maiúsculas** (`MEM`, `X`, `VAR`).

---

## Autômato Finito Determinístico (AFD)

O analisador léxico é implementado como um AFD com estados explícitos:

```
estado_inicial ──dígito/ponto──► estado_numero
               ──letra maiúsc──► estado_identificador
               ──operador──────► estado_operador
               ──parêntese─────► (emite token, retorna)
```

Cada estado é uma função Python. A função `parseExpressao` orquestra as transições até `None` (fim da linha).

Erros detectados pelo AFD:
- Número com dois pontos decimais: `3.14.5`
- Número terminado em ponto: `3.`
- Caractere inválido: `,`, `@`, etc.
- Parênteses desbalanceados

---

## Formato do arquivo de tokens (`tokens.json`)

Gerado automaticamente a cada execução. Contém os tokens da última execução, agrupados por linha:

```json
[
  {
    "linha": 1,
    "tokens": [
      { "tipo": "NUMERO", "valor": "3" },
      { "tipo": "NUMERO", "valor": "4" },
      { "tipo": "OPERADOR", "valor": "+" }
    ]
  },
  ...
]
```

Tipos possíveis: `NUMERO`, `OPERADOR`, `PARENTESE`, `MEMORIA`, `KEYWORD_RES`.

---

## Assembly ARMv7 — detalhes técnicos

O gerador usa **alocação estática de registradores VFP** (`d0`–`d15`) como pilha de compilação:

- Constantes carregadas via `LDR` + `VLDR` da seção `.data`
- Operações: `VADD.F64`, `VSUB.F64`, `VMUL.F64`, `VDIV.F64`
- Divisão inteira (`//`): `VCVT` + `SDIV` + `VCVT` (truncamento em direção a zero)
- Resto (`%`): `SDIV` + `MUL` + `SUB` (sinal do dividendo)
- Potenciação (`^`): loop `VMUL.F64` com contador em `r2`
- Variáveis de memória: `VSTR`/`VLDR` em labels da seção `.data`
- Resultados anteriores (`RES`): carregados via label `_result_N`
- Programa termina em `_halt: B _halt`
