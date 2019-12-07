import threading
import time
from collections import deque

import constants
import shared
import log
import models
import ranking_models
import pickler


class QuestionRankerThreadWorker(threading.Thread):
    def __init__(self, thread_id, questions_segment, query: ranking_models.UserQuery):
        super().__init__()
        self.id = thread_id
        self.questions_segment = questions_segment,
        self.query = query
        self.questions_dict = None

        shared.READY_THREADS_COUNT += 1

    def retrieve_segment(self):
        self.questions_dict = pickler.read_questions_segment(self.questions_segment)
