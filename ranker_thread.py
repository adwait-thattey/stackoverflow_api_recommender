import indexer
import parser
import threading
import time
from collections import deque

import constants
import shared
import log
import models
import ranking_models
import pickler
import ranker_utils
import utils


class QuestionRankerThreadWorker(threading.Thread):
    def __init__(self, thread_id: str, questions_segment: str, query: ranking_models.UserQuery,
                 query_ranker: ranking_models.QueryRanker):
        super().__init__()
        self.id = thread_id
        self.questions_segment = questions_segment
        self.query = query
        self.questions_dict = None
        self.ranker = query_ranker

        shared.READY_THREADS_COUNT += 1

    def retrieve_segment(self):
        self.questions_dict = pickler.read_questions_segment(self.questions_segment)

    def calc_cosine(self, ques_ix: models.QuestionIndex):
        q_cos_dict = ranker_utils.compute_question_cosine(ques_ix, self.query.query_index)
        self.ranker.question_cosines.question_text_cosines.insert_cosine(qid=ques_ix.id, cosine=q_cos_dict["text_cos"])
        self.ranker.question_cosines.question_code_cosines.insert_cosine(qid=ques_ix.id, cosine=q_cos_dict["code_cos"])

        qa_cos_dict = ranker_utils.compute_qa_cosine(ques_ix, self.query.query_index)
        self.ranker.qa_cosines.qa_text_cosines.insert_cosine(qid=ques_ix, cosine=qa_cos_dict["full_text_cos"])

        answers_cosines = ranker_utils.compute_all_answer_cosines(ques_ix, self.query.query_index)
        for acd in answers_cosines:
            self.ranker.answer_cosines.answer_text_cosines.insert_cosine(qid=ques_ix.id, cosine=acd["text_cos"])

    def calc_cosines_for_segment(self):
        for qix in self.questions_dict:
            self.calc_cosine(self.questions_dict[qix])

    def run(self):
        log.debug(f"Starting thread {self.id}")
        shared.ACTIVE_THREADS_COUNT += 1
        log.debug(f"Current running threads: {shared.ACTIVE_THREADS_COUNT}", module="ranker-thread")

        self.retrieve_segment()
        self.calc_cosines_for_segment()
        self.teardown()

        log.debug(f"Stopping thread {self.id}")

    def teardown(self):
        # free up any memory that can be freed
        shared.ACTIVE_THREADS_COUNT -= 1
        pass


class QuestionRankerThread(threading.Thread):
    def __init__(self, thread_id: str, query: ranking_models.UserQuery):
        super().__init__()
        self.thread_id = thread_id
        self.ranker = ranking_models.QueryRanker(query.id)
        self.workers = list()
        self.query = query

    def ret_rank_model(self):
        return self.ranker

    def build_query_index(self):
        query_index = indexer.index_query(self.query)
        self.query.query_index = query_index

    def open_segment_thread(self, segment_id):
        thr = QuestionRankerThreadWorker(self.thread_id + f"_{segment_id}",
                                         questions_segment=segment_id,
                                         query=self.query,
                                         query_ranker=self.ranker
                                         )

        return thr

    def get_all_segments_similarity(self):
        seg_list = utils.get_all_question_segment_lists()

        ix = 0
        while ix < len(seg_list):
            if shared.ACTIVE_THREADS_COUNT < constants.max_parallel_threads:
                thr = self.open_segment_thread(seg_list[ix])
                self.workers.append(thr)
                thr.start()
                ix += 1

            for th in self.workers:
                th.join()

    def run(self):
        self.build_query_index()
        self.get_all_segments_similarity()
        self.teardown()

    def teardown(self):
        # destroy used memory
        pass


if __name__ == "__main__":
    from starter import init, end

    init()
    newq = "6619516"
    fname = f"dataset/questions/raw/{newq}.html"
    q = parser.parse_question_from_file(fname)
    query = ranking_models.UserQuery(title=q.title, text=q.text, code_snippets=[c.snippet for c in q.codes], tags=[])

    thr = QuestionRankerThread(thread_id="main1", query=query)
    query_ranker = thr.ret_rank_model()
    thr.run()
    top_questions = query_ranker.question_cosines.question_text_cosines.get_top()
    top_answers = query_ranker.answer_cosines.answer_text_cosines.get_top()
    top_qa = query_ranker.qa_cosines.qa_text_cosines.get_top()
    end()
