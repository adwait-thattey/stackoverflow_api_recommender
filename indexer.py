import models
import shared
import utils
import parser
import preprocessor
import pickler
import log

import constants


@utils.enforce_types(models.Question)
def index_question(question: models.Question):
    if question.id in shared.INDEXED_QUESTIONS:
        log.debug(f"Question {question.id} already indexed", module="indexer")
        return

    content = preprocessor.preprocess_question_content(question.text)
    ques_index = models.QuestionIndex(question)

    tf_dict = dict()
    for word in content.split(' '):
        if word not in tf_dict:
            tf_dict[word] = 0

        tf_dict[word] += 1

    ques_index.text_index.vector = tf_dict
    ques_index.text_index.calc_magnitude()
    shared.INDEXED_QUESTIONS[question.id] = ques_index

    # print(content)


if __name__ == "__main__":
    from starter import init, end

    init()
    f1 = "dataset/questions/raw/6619516.html"
    q1 = parser.parse_question_from_file(f1)
    index_question(q1)

    f2 = "dataset/questions/raw/15796781.html"

    q2 = parser.parse_question_from_file(f2)
    # log.debug(q2.__dict__, module="indexer")
    index_question(q2)

    pickler.write_questions_index()
    end()
