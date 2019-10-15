from cs50 import get_int


while True:
    s = get_int("Height: ")
    if s >= 1 and s <= 8:
        break

for i in range(s):
    hashes = i + 1
    spaces = s - i - 1

    print(" " * spaces, end="")
    print("#" * hashes)