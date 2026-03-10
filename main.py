import sys

def parseExpressao():
    argument = sys.argv[1]
    with open(argument) as file:
        for line in file:
            print(line)

if __name__ == "__main__":
    parseExpressao()



