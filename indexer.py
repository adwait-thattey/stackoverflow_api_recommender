import models, ranking_models
import shared
import utils
import parser
import preprocessor
import pickler
import log

import constants


@utils.enforce_types(models.QuestionIndex, set)
def calculate_answers_tdf(qix: models.QuestionIndex, question_processed_terms: set):
    tdf = shared.TERM_DOCUMENT_FREQUENCY
    q_processed_terms = question_processed_terms.copy()
    a_processed_terms = set()
    for aix in qix.answers_index:
        for term in aix.text.vector:
            if term not in a_processed_terms:
                tdf.add_answers_term(term)
                if term not in q_processed_terms:
                    tdf.add_qa_term(term)
                    q_processed_terms.add(term)
                a_processed_terms.add(term)

        for term in aix.code.vector:
            if term not in a_processed_terms:
                tdf.add_answers_term(term)
                if term not in q_processed_terms:
                    tdf.add_qa_term(term)
                    q_processed_terms.add(term)
                a_processed_terms.add(term)


@utils.enforce_types(models.QuestionIndex)
def calculate_question_tdf(qix: models.QuestionIndex):
    question_processed_terms = set()
    tdf = shared.TERM_DOCUMENT_FREQUENCY
    if not isinstance(tdf, ranking_models.DocumentTermFrequency):
        raise AssertionError("blah")

    for term in qix.title_index.vector:
        if term in question_processed_terms:
            continue
        tdf.add_questions_term(term)
        tdf.add_qa_term(term)

        question_processed_terms.add(term)

    for term in qix.text_index.vector:
        if term in question_processed_terms:
            continue
        tdf.add_questions_term(term)
        tdf.add_qa_term(term)

        question_processed_terms.add(term)

    for term in qix.code_index.vector:
        if term in question_processed_terms:
            continue
        tdf.add_questions_term(term)
        tdf.add_qa_term(term)

        question_processed_terms.add(term)

    calculate_answers_tdf(qix, question_processed_terms)


def calculate_all_questions_tdf():
    computed = set()

    for qid in shared.QUESTION_SEGMENT_MAP:
        if qid in computed:
            continue

        seg_id = shared.QUESTION_SEGMENT_MAP[qid]
        seg_questions = pickler.read_questions_segment(seg_id)
        for qid in seg_questions:
            if qid in computed:
                continue

            calculate_question_tdf(seg_questions[qid])
            computed.add(qid)


def calculate_all_idf():
    if shared.TERM_DOCUMENT_FREQUENCY:
        del shared.TERM_DOCUMENT_FREQUENCY

    shared.TERM_DOCUMENT_FREQUENCY = ranking_models.DocumentTermFrequency()

    calculate_all_questions_tdf()

    if shared.INVERSE_DOCUMENT_FREQUENCY:
        del shared.INVERSE_DOCUMENT_FREQUENCY

    shared.INVERSE_DOCUMENT_FREQUENCY = ranking_models.InverseDocumentFrequency()

    shared.INVERSE_DOCUMENT_FREQUENCY.compute_idf()


@utils.enforce_types(str)
def index_text(text: str):
    bag_of_words = preprocessor.preprocess_question_content(text)
    tf_dict = dict()
    for word in bag_of_words:
        if word not in tf_dict:
            tf_dict[word] = 0

        tf_dict[word] += 1

    return tf_dict


def index_code_snippets(code_snippets: list):
    tf_dict = dict()

    for snip in code_snippets:
        bag_of_words = preprocessor.preprocess_code_snippet(snip.snippet)
        for word in bag_of_words:
            if word not in tf_dict:
                tf_dict[word] = 0

            tf_dict[word] += 1

    return tf_dict


@utils.enforce_types(models.Question)
def index_question(question: models.Question):
    if question.id in shared.INDEXED_QUESTIONS:
        log.debug(f"Question {question.id} already indexed", module="indexer")
        return

    ques_index = models.QuestionIndex(question)

    title_index = index_text(question.title)
    content_index = index_text(question.text)
    code_index = index_code_snippets(question.codes)

    ques_index.title_index.vector = title_index
    ques_index.title_index.calc_magnitude()

    ques_index.text_index.vector = content_index
    ques_index.text_index.calc_magnitude()

    ques_index.code_index.vector = code_index
    ques_index.code_index.calc_magnitude()

    for ans in question.answers:
        ans_index = models.AnswerIndex(qid=question.id)
        text_index = index_text(ans.text)
        code_index = index_code_snippets(ans.codes)

        ans_index.text.vector = text_index
        ans_index.text.calc_magnitude()

        ans_index.code.vector = code_index
        ans_index.code.calc_magnitude()

        ques_index.answers_index.append(ans_index)

    if question.id not in shared.QUESTION_SEGMENT_MAP:
        shared.TOTAL_QUESTIONS += 1
        shared.TOTAL_ANSWERS += len(question.answers)

    return ques_index
    # print(content)

@utils.enforce_types(models.APIDoc)
def index_api_doc(api: models.APIDoc):

    api_index = models.APIDocIndex(api)

    api_text_index = index_text(api.text)
    api_combined_text = api.text

    api_all_code_snippets = api.codes
    api_all_code_snippets.extend([api.name, api.module, api.package])
    api_code_index = index_code_snippets(api_all_code_snippets)

    api_combined_code_snippets = api_all_code_snippets

    api_index.text_index.vector = api_text_index
    api_index.text_index.calc_magnitude()

    api_index.code_index.vector = api_code_index
    api_index.code_index.calc_magnitude()


    for method in api.methods:
        method_index = models.MethodIndex(api.name)

        method_codes = [method.method_name,method.method_sig]
        method_code_index = index_code_snippets(method_codes)
        api_combined_code_snippets.extend(method_codes)

        method_text = method.description
        method_text_index = index_text(method_text)
        api_combined_text = api_combined_text + " " + method_text


        method_index.text_index.vector = method_text_index
        method_index.text_index.calc_magnitude()

        method_index.code_index.vector = method_code_index
        method_index.code_index.calc_magnitude()

        api_index.methods_index.append(method_index)

    api_combined_text_index = index_text(api_combined_text)
    api_combined_code_snippets_index = index_code_snippets(api_combined_code_snippets)

    api_index.combined_text_index.vector = api_combined_text_index
    api_index.combined_code_index.vector = api_combined_code_snippets_index

    if api.name not in shared.API_SEGMENT_MAP:
        shared.TOTAL_API_DOCS += 1
        shared.TOTAL_API_METHODS += len(api.methods)

    return api_index


if __name__ == "__main__":
    from starter import init, end

    init()
    qindex = dict()
    to_process = ["6619516", "15235400", "15796781"]
    for qid in to_process:
        fname = f"dataset/questions/raw/{qid}.html"
        q = parser.parse_question_from_file(fname)
        qindex[q.id] = index_question(q)

    pickler.write_questions_index(qindex)
    calculate_all_idf()
    end()
