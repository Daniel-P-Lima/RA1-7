import sys


def ler_expressoes(caminho_arquivo: str) -> list[str]:
    expressoes = []

    with open(caminho_arquivo, "r") as arquivo:
        for linha in arquivo:
            linha = linha.strip()

            if linha:
                expressoes.append(linha) # array de strings 

    return expressoes


def main():
    caminho_arquivo = sys.argv[1]

    try:
        expressoes = ler_expressoes(caminho_arquivo)

        for i, expressao in enumerate(expressoes, start=1):
            print(f"Linha {i}: {expressao}")

    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {caminho_arquivo}")
        sys.exit(1)


if __name__ == "__main__":
    main()


