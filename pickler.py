import pickle

import log
import shared
import os
import constants
import utils


def read_questions_segment(segment_id):
    log.log("pickler", f"Reading questions segment {segment_id}")
    questions_dict = None
    with open(os.path.join(constants.pickled_questions_dir, str(segment_id)), 'rb') as f:
        questions_dict = pickle.load(f)

    if questions_dict is not None:

        return questions_dict

    else:
        raise ValueError(f"[DEBUG] [PICKLER] Unable to read questions segment")


def write_questions_segment(segment_id, questions_dict):
    log.log("pickler", f"Writing questions segment {segment_id}")
    with open(os.path.join(constants.pickled_questions_dir, str(segment_id)), 'wb') as f:
        pickle.dump(questions_dict, f)


def write_questions_index(questions_dict=None):
    if questions_dict is None:
        questions_dict = shared.INDEXED_QUESTIONS

    new_segments = 0
    modified_segments = 0
    pickled = set()
    log.log("pickler", f"Writing questions index to pickles ")

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
                log.warn("pickler", f"Segment {segment} in map but does not exist. Removing")
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

    log.log("pickler",
            f"Questions Written to disk. Modified Segments:{modified_segments},  New Segments:{new_segments}")


def read_question_segment_map():
    log.log("pickler", f" Reading question segment map")
    try:
        with open(os.path.join(constants.pickled_questions_dir, "qsmap"), 'rb') as f:
            shared.QUESTION_SEGMENT_MAP = pickle.load(f)
    except FileNotFoundError:
        log.warn("pickler", f" Question-Segment Map pickle file not found")
        shared.QUESTION_SEGMENT_MAP = dict()


def write_question_segment_map():
    log.log("pickler", f" Writing question segment map")
    with open(os.path.join(constants.pickled_questions_dir, "qsmap"), 'wb') as f:
        pickle.dump(shared.QUESTION_SEGMENT_MAP, f)
