import sys


def printf() -> int | None:
    return None


# with (open() as f1, open() as f2):
#     pass

match printf():
    case 1:
        print(1)
    case 2:
        print(2)
    case _:
        print("no")
