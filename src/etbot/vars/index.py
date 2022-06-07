# returns the index from the file
def get_index_from_file() -> int:
    with open("index.txt", 'r', encoding="utf8") as file:
        number = file.read()
    return int(number)


_index: int = get_index_from_file()


def get_index() -> int: return _index


def increment_index() -> None:
    global _index
    _index += 1
    with open("index.txt", 'w', encoding="utf8") as file:
        file.write(str(_index))


def set_index(index: int) -> None:
    global _index
    _index = index
    with open("index.txt", 'w', encoding="utf8") as file:
        file.write(str(_index))
