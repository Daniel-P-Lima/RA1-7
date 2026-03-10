import sys

def parseExpressao(line: str) -> list[str]:
    return line.strip().split()

def openFile():
    argument = sys.argv[1]
    tokens = []
    with open(argument) as file:
        for line in file:
            token = parseExpressao(line)
            tokens.append(token)
        return tokens

if __name__ == "__main__":
    tokens = openFile()
    print(tokens)



