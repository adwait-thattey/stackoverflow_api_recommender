from pickler import read_questions_shared_data, write_questions_shared_data, read_tdf_idf, write_tdf_idf, read_api_shared_data, write_api_shared_data
from utils import gen_stopwords
import log


def init():
    """
    Performs following init tasks
        - load question-map from disk
        - init stop words
    """
    log.log(f"Running init tasks", module="starter")

    read_api_shared_data()
    read_questions_shared_data()
    read_tdf_idf()
    gen_stopwords()


def end():
    """
    Performs the following end tasks
        - write question-segment map to disk

    """
    log.log(f" Running teardown tasks", module="starter")

    write_api_shared_data()
    write_questions_shared_data()
    write_tdf_idf()
