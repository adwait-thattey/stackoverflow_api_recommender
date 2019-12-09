import pickle

import log
import shared
import os
import constants
import utils


def read_questions_segment(segment_id):
    log.log(f"Reading questions segment {segment_id}", module="pickler")
    questions_dict = None
    with open(os.path.join(constants.pickled_questions_dir, str(segment_id) + constants.pickle_files_extension),
              'rb') as f:
        questions_dict = pickle.load(f)

    if questions_dict is not None:

        return questions_dict

    else:
        raise ValueError(f"[DEBUG] [PICKLER] Unable to read questions segment")


def write_questions_segment(segment_id, questions_dict):
    log.log(f"Writing questions segment {segment_id}", module="pickler")
    with open(os.path.join(constants.pickled_questions_dir, str(segment_id) + constants.pickle_files_extension),
              'wb') as f:
        pickle.dump(questions_dict, f)


def write_questions_index(questions_dict=None):
    if questions_dict is None:
        questions_dict = shared.INDEXED_QUESTIONS

    new_segments = 0
    modified_segments = 0
    pickled = set()
    log.log(f"Writing questions index to pickles ", module="pickler")

    new_segment_questions_ids = set()
    for ques_id in questions_dict:
        if ques_id in pickled:
            continue

        if ques_id in shared.QUESTION_SEGMENT_MAP:
            # question is already indexed. update index
            segment = shared.QUESTION_SEGMENT_MAP[ques_id]
            try:
                segment_questions = read_questions_segment(segment)
                # get list of questions in questions_dict which are not yet indexed and in this segment
                q_seg_ids = [qid for qid in questions_dict if qid not in pickled and qid in segment_questions]

                for i in q_seg_ids:
                    segment_questions[i] = questions_dict[i]

                write_questions_segment(segment, segment_questions)
                modified_segments += 1
                pickled.update(q_seg_ids)
            except FileNotFoundError:
                log.warn(f"Segment {segment} in map but does not exist. Removing", module="pickler")
                shared.QUESTION_SEGMENT_MAP = {k: v for (k, v) in shared.QUESTION_SEGMENT_MAP.items() if v != segment}

        if ques_id not in shared.QUESTION_SEGMENT_MAP:
            # question is not indexed yet. Create new segments
            new_segment_questions_ids.add(ques_id)
            pickled.add(ques_id)
            if len(new_segment_questions_ids) >= constants.questions_per_segment:
                # write this seg
                new_seg_questions = {qid: questions_dict[qid] for qid in new_segment_questions_ids}
                new_seg_id = utils.get_new_question_segment_id()
                write_questions_segment(new_seg_id, new_seg_questions)
                new_segments += 1
                for qid in new_segment_questions_ids:
                    shared.QUESTION_SEGMENT_MAP[qid] = new_seg_id

                new_segment_questions_ids.clear()

    if new_segment_questions_ids:
        # some questions are yet to be written
        new_seg_questions = {qid: questions_dict[qid] for qid in new_segment_questions_ids}
        new_seg_id = utils.get_new_question_segment_id()
        write_questions_segment(new_seg_id, new_seg_questions)
        new_segments += 1
        for qid in new_segment_questions_ids:
            shared.QUESTION_SEGMENT_MAP[qid] = new_seg_id

        new_segment_questions_ids.clear()

    log.log(f"Questions Written to disk. Modified Segments:{modified_segments},  New Segments:{new_segments}",
            module="pickler")


def read_shared_data():
    log.log(f" Reading question segment map", module="pickler")
    try:
        with open(os.path.join(constants.pickled_questions_dir, "qsmap" + constants.pickle_files_extension), 'rb') as f:
            shared.QUESTION_SEGMENT_MAP = pickle.load(f)

        log.log("Reading Total Counts")
        try:
            with open(os.path.join(constants.pickle_data_dir, "counts" + constants.pickle_files_extension), 'rb') as f2:
                counts = pickle.load(f2)
                shared.TOTAL_QUESTIONS = counts['TOTAL_QUESTIONS']
                shared.TOTAL_ANSWERS = counts['TOTAL_ANSWERS']
                shared.TOTAL_API_DOCS = counts['TOTAL_API_DOCS']
                shared.TOTAL_API_METHODS = counts['TOTAL_API_METHODS']
        except FileNotFoundError:
            log.fail(
                "The question-seg map pickle exists but total_counts does not. This will lead to inconsistencies in IDF. Delete the seg map ",
                module="pickler")
            exit()
    except FileNotFoundError:
        log.warn(f" Question-Segment Map pickle file not found", module="pickler")
        shared.QUESTION_SEGMENT_MAP = dict()

    try:
        log.log(f" Reading Term Questions Dict", module="pickler")
        with open(os.path.join(constants.pickle_data_dir, "tqd" + constants.pickle_files_extension), 'rb') as f:
            shared.TERM_QUESTIONS_DICT = pickle.load(f)

        log.log(f" Reading Term API Dict", module="pickler")
        with open(os.path.join(constants.pickle_data_dir, "tad" + constants.pickle_files_extension), 'rb') as f:
            shared.TERM_API_DOC_DICT = pickle.load(f)

    except FileNotFoundError:
        log.fail(f"Term Questions or API Dict Pickle object not found", module="pickler")


def write_shared_data():
    log.log(f" Writing question segment map", module="pickler")
    with open(os.path.join(constants.pickled_questions_dir, "qsmap" + constants.pickle_files_extension), 'wb') as f:
        pickle.dump(shared.QUESTION_SEGMENT_MAP, f)

    count = {
        "TOTAL_QUESTIONS": shared.TOTAL_QUESTIONS,
        "TOTAL_ANSWERS": shared.TOTAL_ANSWERS,
        "TOTAL_API_DOCS": shared.TOTAL_API_DOCS,
        "TOTAL_API_METHODS": shared.TOTAL_API_METHODS
    }
    log.log("Writing total counts")
    with open(os.path.join(constants.pickle_data_dir, "counts" + constants.pickle_files_extension), 'wb') as f:
        pickle.dump(count, f)

    log.log(f"Writing Term Questions Dict", module="pickler")
    with open(os.path.join(constants.pickle_data_dir, "tqd" + constants.pickle_files_extension), 'wb') as f:
        pickle.dump(shared.TERM_QUESTIONS_DICT, f)

    log.log(f"Writing API DOCS Dict", module="pickler")
    with open(os.path.join(constants.pickle_data_dir, "tad" + constants.pickle_files_extension), 'wb') as f:
        pickle.dump(shared.TERM_API_DOC_DICT, f)


def write_tdf_idf():
    log.log(f" Writing TDF-IDF pickles", module="pickler")
    with open(os.path.join(constants.pickle_data_dir, "tdf" + constants.pickle_files_extension), 'wb') as f:
        pickle.dump(shared.TERM_DOCUMENT_FREQUENCY, f)

    with open(os.path.join(constants.pickle_data_dir, "idf" + constants.pickle_files_extension), 'wb') as f:
        pickle.dump(shared.INVERSE_DOCUMENT_FREQUENCY, f)


def read_tdf_idf():
    log.log(f" Reading TDF-IDF Pickles", module="pickler")
    try:
        with open(os.path.join(constants.pickle_data_dir, "tdf" + constants.pickle_files_extension), 'rb') as f:
            shared.TERM_DOCUMENT_FREQUENCY = pickle.load(f)

        with open(os.path.join(constants.pickle_data_dir, "idf" + constants.pickle_files_extension), 'rb') as f:
            shared.INVERSE_DOCUMENT_FREQUENCY = pickle.load(f)

    except FileNotFoundError:
        log.warn(f"tdf-idf pickle files not found", module="pickler")
