from cs50 import get_string
from sys import argv


def main():
    if len(argv) != 2:
        print("Usage: python caesar.py k")
        exit(1)

    k = int(argv[1])
    plaintext = get_string("plaintext: ")
    print("ciphertext: ", end="")

    for c in plaintext:
        if not c.isalpha():
            print(c, end="")
            continue

        if c.isupper():
            offset = 65
        else:
            offset = 97

        pi = ord(c) - offset
        ci = (pi + k) % 26

        print(chr(ci + offset), end="")

    print()

    return 0


if __name__ == "__main__":
    main()