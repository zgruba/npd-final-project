import argparse
from lib import hello

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "name",
        type=str,
        help="Enter your name"
    )

    parser.add_argument(
        "size",
        type=int,
        help="Enter size of the matrix"
    )

    args = parser.parse_args()

    hello(args.name, args.size)


if __name__ == "__main__":
    main()