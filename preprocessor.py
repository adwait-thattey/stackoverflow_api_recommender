"""
This module separates files into smaller units each containing no more than 10k characters.
Then removes special characters and everything within brackets

"""
import os

import log
import shared
import constants
from unidecode import unidecode
from string import punctuation
from collections import OrderedDict
from nltk.stem.porter import PorterStemmer

DOC_DIR_PATH = ""
stemmer = PorterStemmer()


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


def process_text_word(word: str):
    # if word.isdigit() or not word.isalnum():
    #     return constants.null_word
    word = word.lower()

    if word in shared.STOP_WORDS:
        return ""

    stemmed_word = stemmer.stem(word)

    if stemmed_word != word:
        # log.debug(f"Stemmed {word} to {stemmed_word}", module="preprocessor")
        pass

    word = stemmed_word # comment this to remove stemming
    return word


def process_code_word(word: str):
    # if word.isdigit() or not word.isalnum():
    #     return constants.null_word

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
    words = [process_text_word(w) for w in line.split()]
    line = " ".join([w for w in words if w])
    # line = line.replace("  ", " ")  # remove duplicate spaces
    words = [w for w in words if w]
    return words


def process_code_line(code_line):
    line = unidecode(code_line)

    line = "".join([c if c not in constants.code_replaceable_special_characters else ' ' for c in line])
    words = [process_code_word(w) for w in line.split()]
    return ([w for w in words if w])


def preprocess_question_content(content: str):
    lines = break_multiple_lines(content)
    bag_of_words = list()
    [bag_of_words.extend(process_line(l)) for l in lines]
    return bag_of_words


def preprocess_code_snippet(snippet):
    lines = snippet.split('\n')
    bag_of_words = list()
    [bag_of_words.extend(process_code_line(l)) for l in lines]

    return bag_of_words


if __name__ == "__main__":
    pass
    # preprocess_document("part_3", ".txt")
