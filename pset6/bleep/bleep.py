from cs50 import get_string
from sys import argv


def main():

    while True:
        if len(argv) != 2:
            print("Usage: python bleep.py dictionary")
            exit(1)
        else:
            break

    s = get_string("What message would you like to censor?\n")
    message = s.split()

    words = set()
    infile = open(argv[1], 'r')

    for line in infile:
        words.add(line.rstrip("\n"))
    infile.close()

    censorMessage = []

    for i in range(len(message)):
        if message[i].lower() in words:
            censorWord = list(message[i])
            for j in range(len(censorWord)):
                censorWord[j] = "*"
            censorMessage.append("".join(censorWord))
        else:
            censorMessage.append(message[i])

    print(" ".join(censorMessage))


if __name__ == "__main__":
    main()
