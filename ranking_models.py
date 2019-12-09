import heapq

import constants
import models
import utils
import shared
import random
import math


class Cosine:
    def __init__(self, obj_id, cosine, type):
        self.id = obj_id
        self.cosine = cosine
        self.type = type

    def __lt__(self, other):
        return self.cosine < other.cosine


class CosineMaxHeap:
    def __init__(self):
        self._data = list()
        # heapq.heapify(self._data)

    def push(self, obj: Cosine):
        obj.cosine *= -1
        heapq.heappush(self._data, obj)

    def pop(self):
        obj = heapq.heappop(self._data)
        obj.cosine *= -1
        return obj

    def heapify(self):
        heapq.heapify(self._data)

    def __len__(self):
        return len(self._data)


class GenericCosines:
    def __init__(self, query_id, type):
        self.query_id = query_id
        self.cosines = CosineMaxHeap()
        self.cosine_sum = float(0)
        self.type = type

    def insert_cosine(self, qid, cosine):
        cosine_obj = Cosine(obj_id=qid, cosine=cosine, type="question")
        self.cosines.push(cosine_obj)
        self.cosine_sum += cosine

    def get_top(self):
        while len(self.cosines) > 0:
            obj = self.cosines.pop()
            self.cosine_sum -= obj.cosine
            yield obj

    @property
    def avg_cosine(self):
        return self.cosine_sum / len(self.cosines)


class QuestionCosines:
    def __init__(self, query_id):
        # the text cosines comprise of both title and description
        self.question_text_cosines = GenericCosines(query_id, type="question_text")
        self.question_code_cosines = GenericCosines(query_id, type="question_code")
        self.question_joint_cosines = GenericCosines(query_id, type="question_joint")


class AnswerCosines:
    def __init__(self, query_id):
        self.answer_text_cosines = GenericCosines(query_id, type="answer_text")
        self.answer_code_cosines = GenericCosines(query_id, type="answer_code")
        self.answer_joint_cosines = GenericCosines(query_id, type="answer_joint")


class QAJointCosines:
    def __init__(self, query_id):
        self.qa_text_cosines = GenericCosines(query_id, type="qa_text")
        self.qa_code_cosines = GenericCosines(query_id, type="qa_code")
        self.qa_joint_cosines = GenericCosines(query_id, type="qa_joint")


class APIDocCosines:
    def __init__(self, query_id):
        # doc cosines combine API and its field description
        self.doc_text_cosines = GenericCosines(query_id=query_id, type="doc_text")
        self.doc_code_cosines = GenericCosines(query_id=query_id, type="doc_code")
        self.doc_joint_cosines = GenericCosines(query_id=query_id, type="doc_joint")


class APIMethodCosines:
    def __init__(self, query_id):
        self.method_text_cosines = GenericCosines(query_id=query_id, type="method_text")
        self.method_code_cosines = GenericCosines(query_id=query_id, type="method_code")
        self.method_joint_cosines = GenericCosines(query_id=query_id, type="method_joint")


class APIDMCosines:
    def __init__(self, query_id):
        self.dm_text_cosines = GenericCosines(query_id=query_id, type="dm_text")
        self.dm_code_cosines = GenericCosines(query_id=query_id, type="dm_code")
        self.dm_joint_cosines = GenericCosines(query_id=query_id, type="dm_joint")


class QueryRanker:
    def __init__(self, query_id):
        self.question_cosines = QuestionCosines(query_id)
        self.answer_cosines = AnswerCosines(query_id)
        self.qa_cosines = QAJointCosines(query_id)

        self.doc_cosines = APIDocCosines(query_id)
        self.method_cosines = APIMethodCosines(query_id)
        self.dm_cosines = APIDMCosines(query_id)


class DocumentTermFrequency:
    def __init__(self):
        self.questions = dict()
        self.answers = dict()
        self.qa = dict()
        self.api_doc = dict()
        self.api_methods = dict()
        self.api_dm = dict()

    def add_questions_term(self, term):
        if term not in self.questions:
            self.questions[term] = 0

        self.questions[term] += 1

    def add_answers_term(self, term):
        if term not in self.answers:
            self.answers[term] = 0

        self.answers[term] += 1

    def add_qa_term(self, term):
        if term not in self.qa:
            self.qa[term] = 0

        self.qa[term] += 1

    def add_apidoc_term(self, term):
        if term not in self.api_doc:
            self.api_doc[term] = 0

        self.api_doc[term] += 1

    def add_apimethods_term(self, term):
        if term not in self.api_methods:
            self.api_methods[term] = 0

        self.api_methods[term] += 1

    def add_apidm_term(self, term):
        if term not in self.api_dm:
            self.api_dm[term] = 0

        self.api_dm[term] += 1


class InverseDocumentFrequency:
    def __init__(self):
        self.updated_terms = set()
        self.questions = dict()
        self.answers = dict()
        self.qa = dict()
        self.api_doc = dict()
        self.api_methods = dict()
        self.api_dm = dict()

    def compute_idf(self):
        # questions
        tdf = shared.TERM_DOCUMENT_FREQUENCY
        for term in tdf.questions:
            self.questions[term] = math.log((shared.TOTAL_QUESTIONS + 1) / (tdf.questions[term] + 1),
                                            constants.log_base)
        for term in tdf.answers:
            self.answers[term] = math.log((shared.TOTAL_ANSWERS + 1) / (tdf.answers[term] + 1), constants.log_base)

        for term in tdf.qa:
            self.qa[term] = math.log((shared.TOTAL_QUESTIONS + 1) / (tdf.qa[term] + 1), constants.log_base)

        for term in tdf.api_doc:
            self.api_doc[term] = math.log((shared.TOTAL_API_DOCS + 1) / (tdf.api_doc[term] + 1),
                                          constants.log_base)
        for term in tdf.api_methods:
            self.api_methods[term] = math.log((shared.TOTAL_API_METHODS + 1) / (tdf.api_methods[term] + 1),
                                              constants.log_base)
        for term in tdf.api_dm:
            self.api_dm[term] = math.log((shared.TOTAL_API_DOCS + 1) / (tdf.api_dm[term] + 1), constants.log_base)

        self.updated_terms.clear()

    def recompute_idf(self):
        tdf = shared.TERM_DOCUMENT_FREQUENCY
        for term in self.updated_terms:
            if term in tdf.questions:
                self.questions[term] = math.log((1 + shared.TOTAL_QUESTIONS) / (1 + tdf.questions[term]),
                                                constants.log_base)
            if term in tdf.answers:
                self.answers[term] = math.log((1 + shared.TOTAL_ANSWERS) / (1 + tdf.answers[term]),
                                              constants.log_base)

            if term in tdf.qa:
                self.qa[term] = math.log((1 + shared.TOTAL_QUESTIONS) / (1 + tdf.qa[term]), constants.log_base)

            if term in tdf.api_doc:
                self.api_doc[term] = math.log((1 + shared.TOTAL_API_DOCS) / (1 + tdf.api_doc[term]),
                                              constants.log_base)
            if term in tdf.api_methods:
                self.api_methods[term] = math.log((1 + shared.TOTAL_API_METHODS) / (1 + tdf.api_methods[term]),
                                                  constants.log_base)
            if term in tdf.api_dm:
                self.api_dm[term] = math.log((1 + shared.TOTAL_API_DOCS) / (1 + tdf.api_dm[term]),
                                             constants.log_base)


class UserQueryIndex:
    def __init__(self, query_id):
        self.id = query_id
        self.title_index = models.Index()
        self.text_index = models.Index()
        self.title_text_index = models.Index()
        self.code_index = models.Index()
        self.others_index = models.Index()


class UserQuery:
    def __init__(self, title, text, code_snippets, tags):
        self.id = str(random.randint(1, 100))
        while self.id in shared.ACTIVE_QUERIES:
            self.id = str(random.randint(1, 100))

        self.title = title
        self.text = text
        self.codes = [models.CodeSnippet("java", cs) for cs in code_snippets]
        self.tags = tags
        self.query_index = UserQueryIndex(self.id)
        self.ranker = QueryRanker(self.id)
