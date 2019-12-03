from pickler import read_question_segment_map, write_question_segment_map
from utils import gen_stopwords
import log


def init():
    """
    Performs following init tasks
        - load question-map from disk
        - init stop words
    """
    log.log("starter", f"Running init tasks")
    read_question_segment_map()
    gen_stopwords()


def end():
    """
    Performs the following end tasks
        - write question-segment map to disk

    """
    log.log("starter", f" Running teardown tasks")

    write_question_segment_map()
