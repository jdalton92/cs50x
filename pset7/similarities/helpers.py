from nltk.tokenize import sent_tokenize


def lines(a, b):
    """Return lines in both a and b"""

    a_line = set(a.split("\n"))
    b_line = set(b.split("\n"))

    return list(a_line & b_line)


def sentences(a, b):
    """Return sentences in both a and b"""

    a_sentence = set(sent_tokenize(a))
    b_sentence = set(sent_tokenize(b))

    return list(a_sentence & b_sentence)


def substring_split(string, n):
    """Return a list of substrings of length n"""

    substrings = []
    for i in range(len(string) - n + 1):
        substrings.append(string[i:i + n])

    return substrings


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""

    a_substring = set(substring_split(a, n))
    b_substring = set(substring_split(b, n))

    return list(a_substring & b_substring)