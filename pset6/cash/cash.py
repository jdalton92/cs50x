from cs50 import get_float


def main():
    while True:
        dollars = get_float("Change owed: ")
        cents = dollars * 100
        if cents > 0:
            break

    quarters = cents // 25
    dimes = (cents % 25) // 10
    nickels = ((cents % 25) % 10) // 5
    pennies = ((cents % 25) % 10) % 5

    print(f"{quarters + dimes + nickels + pennies}")


if __name__ == "__main__":
    main()
