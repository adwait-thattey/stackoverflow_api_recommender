import constants
import os

import log
import shared
import nltk
import random


def enforce_types(*types, return_type=None):
    def decorator(f):
        def new_f(*args, **kwds):
            # we need to convert args into something mutable
            for (a, t) in zip(args, types):
                if not isinstance(a, t):
                    raise TypeError(" [Enforced Types]: Arguments of wrong type passed to function")
                # feel free to have more elaborated convertion
            result = f(*args, **kwds)
            if return_type:
                if not isinstance(result, return_type):
                    raise TypeError(
                        f" [Enforced Types]: Function returned wrong type \n Expected {repr(return_type)}. Received {type(result)} ")

            return result

        return new_f

    return decorator


def gen_stopwords():
    log.log(f"generating Stop Words", module="utils")
    try:
        stopwords = nltk.corpus.stopwords
        stop_words = set(stopwords.words('english'))
        shared.STOP_WORDS = stop_words
    except LookupError:
        nltk.download('stopwords')
        log.log(
            f"Could not generate stop words. Downloaded the nltk english dataset. \n Recommended to close and run program again \n Press Enter to continue",
            module="utils")
        input()


def get_new_question_segment_id():
    file_list = [f for f in os.listdir(constants.pickled_questions_dir) if
                 os.path.isfile(os.path.join(constants.pickled_questions_dir, f))]

    start = 1
    while f"{str(start)}{constants.pickle_files_extension}" in file_list:
        start += 1

    return start


def get_all_question_segment_lists():
    file_list = [f for f in os.listdir(constants.pickled_questions_dir) if
                 os.path.isfile(os.path.join(constants.pickled_questions_dir, f))]

    file_list = [f.strip('.pickle') for f in file_list if f.split('.')[0].isdigit()]

    return file_list


if __name__ == "__main__":
    print(get_all_question_segment_lists())
