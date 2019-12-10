import copy

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
        log.debug(f"Starting Question Ranker thread {self.id}", module="ranker-thread")
        shared.ACTIVE_THREADS_COUNT += 1
        log.debug(f"Current running threads: {shared.ACTIVE_THREADS_COUNT}", module="ranker-thread")

        self.retrieve_segment()
        self.calc_cosines_for_segment()
        self.teardown()

    def teardown(self):
        # free up any memory that can be freed
        log.debug(f"Stopping Question thread {self.id}")
        shared.ACTIVE_THREADS_COUNT -= 1
        pass


class APIRankerThreadWorker(threading.Thread):
    def __init__(self, thread_id: str, api_segment: str, query: ranking_models.UserQuery,
                 query_ranker: ranking_models.QueryRanker):
        super().__init__()
        self.id = thread_id
        self.api_segment = api_segment
        self.query = query
        self.api_dict = None
        self.ranker = query_ranker

        shared.READY_THREADS_COUNT += 1

    def retrieve_segment(self):
        self.api_dict = pickler.read_api_docs_segment(self.api_segment)

    def calc_cosine(self, api_ix: models.APIDocIndex):
        api_cos_dict = ranker_utils.compute_api_cosine(api_ix, self.query.query_index)
        self.ranker.doc_cosines.doc_text_cosines.insert_cosine(qid=api_ix.name.snippet, cosine=api_cos_dict["text_cos"])
        self.ranker.doc_cosines.doc_code_cosines.insert_cosine(qid=api_ix.name.snippet, cosine=api_cos_dict["code_cos"])

        apidm_cos_dict = ranker_utils.compute_apidm_cosine(api_ix, self.query.query_index)
        self.ranker.dm_cosines.dm_text_cosines.insert_cosine(qid=api_ix.name.snippet, cosine=apidm_cos_dict["full_text_cos"])

        methods_cosines = ranker_utils.compute_all_methods_cosines(api_ix, self.query.query_index)
        for mc in methods_cosines:
            self.ranker.method_cosines.method_text_cosines.insert_cosine(qid=api_ix.name.snippet, cosine=mc["text_cos"])

    def calc_cosines_for_segment(self):
        for apiname in self.api_dict:
            self.calc_cosine(self.api_dict[apiname])

    def run(self):
        log.debug(f"Starting API Ranker thread {self.id}", module="ranker-thread")
        shared.ACTIVE_THREADS_COUNT += 1
        log.debug(f"Current running threads: {shared.ACTIVE_THREADS_COUNT}", module="ranker-thread")

        self.retrieve_segment()
        self.calc_cosines_for_segment()
        self.teardown()

    def teardown(self):
        # free up any memory that can be freed
        log.debug(f"Stopping API thread {self.id}")
        shared.ACTIVE_THREADS_COUNT -= 1
        pass


class QuestionRankerThread(threading.Thread):
    def __init__(self, thread_id: str, query: ranking_models.UserQuery):
        super().__init__()
        self.thread_id = thread_id
        self.ranker = ranking_models.QueryRanker(query.id)
        self.workers = list()
        self.query = copy.deepcopy(query)

    def ret_rank_model(self):
        return self.ranker

    def build_query_index(self):
        query_index = indexer.index_query(self.query, shared.INVERSE_DOCUMENT_FREQUENCY.qa)
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


class APIRankerThread(threading.Thread):
    def __init__(self, thread_id: str, query: ranking_models.UserQuery, ranker=None):
        super().__init__()
        self.thread_id = thread_id
        self.ranker = ranker if ranker else ranking_models.QueryRanker(query.id)
        self.workers = list()
        self.query = copy.deepcopy(query)

    def ret_rank_model(self):
        return self.ranker

    def build_query_index(self):
        query_index = indexer.index_query(self.query, shared.INVERSE_DOCUMENT_FREQUENCY.api_dm)
        self.query.query_index = query_index

    def open_segment_thread(self, segment_id):
        thr = APIRankerThreadWorker(self.thread_id + f"_{segment_id}",
                                    api_segment=segment_id,
                                    query=self.query,
                                    query_ranker=self.ranker
                                    )

        return thr

    def get_all_segments_similarity(self):
        seg_list = utils.get_all_api_segment_lists()

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

    thr = APIRankerThread(thread_id="main1", query=query)
    query_ranker = thr.ret_rank_model()
    thr.run()
    top_apis = query_ranker.doc_cosines.doc_text_cosines.get_top()
    top_methods = query_ranker.method_cosines.method_text_cosines.get_top()
    top_apidm = query_ranker.dm_cosines.dm_text_cosines.get_top()
    end()
