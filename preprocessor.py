"""
This module separates files into smaller units each containing no more than 10k characters.
Then removes special characters and everything within brackets

"""
import os

import shared
import constants
from unidecode import unidecode
from string import punctuation
from collections import OrderedDict

DOC_DIR_PATH = ""


def remove_enclosed_content(line):
    # removes all content enclosed by brackets {} [] ()
    ret = ''
    skip1c = 0
    skip2c = 0
    skip3c = 0
    for i in line:
        if i == '[':
            skip1c += 1
        elif i == '(':
            skip2c += 1
        elif i == '{':
            skip3c += 1
        elif i == ']' and skip1c > 0:
            skip1c -= 1
        elif i == ')' and skip2c > 0:
            skip2c -= 1
        elif i == '}':
            skip3c -= 1
        elif skip1c == 0 and skip2c == 0 and skip3c == 0:
            ret += i

    return ret


def break_multiple_lines(line):
    lines = line.split('\n')
    ret_lines = list()
    for l in lines:
        l.strip().strip('.')
        start = 0
        ix = 0
        while ix < len(l):
            if l[ix] == '.':
                if ix == len(l) - 1 or l[ix + 1] == ' ':
                    ret_lines.append(l[start:ix])
                    start = ix + 2

            ix += 1
        else:
            ret_lines.append(l[start:-1])

    return ret_lines


def process_word(word: str):
    # if word.isdigit() or not word.isalnum():
    #     return constants.null_word
    word = word.lower()

    if word in shared.STOP_WORDS:
        return ""

    return word


def replace_special_meaning_symbols(line):
    if not constants.punctuations:
        constants.punctuations = set(punctuation)

    replace_dict = OrderedDict([
        (',', '\n'),
        ("'s", " is"),
        ("'m", " am"),
        ("can't", "can not"),
        ("n't", " not"),
        ("'ll", " will")
    ])

    def replace_all(text, dic):
        for i, j in dic.items():
            text = text.replace(i, j)
        return text

    line = replace_all(line, replace_dict)
    return line


def process_line(line):
    line = unidecode(line)
    line = line.strip().strip('.').strip()
    line = replace_special_meaning_symbols(line)
    line = "".join([c if c not in constants.question_replaceable_special_characters else ' ' for c in line])
    words = [process_word(w) for w in line.split()]
    line = " ".join([w for w in words if w])
    line = line.replace("  ", " ")  # remove duplicate spaces

    return line


def preprocess_question_content(content):
    lines = break_multiple_lines(content)
    processed_lines = [process_line(l) for l in lines]
    return " ".join([l for l in processed_lines if l])


if __name__ == "__main__":
    pass
    # preprocess_document("part_3", ".txt")
