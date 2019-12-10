from copy import deepcopy

import models, ranking_models
import shared
import utils
import parser
import preprocessor
import pickler
import log

import constants


def combine_title_text_index(text_index: models.Index, title_index: models.Index):
    combined_index = deepcopy(text_index)

    for term in title_index.vector:
        if term not in combined_index.vector:
            combined_index.vector[term] = 0

        combined_index.vector[term] += 2 * title_index.vector[term]

    return combined_index


@utils.enforce_types(models.APIDocIndex, set)
def calculate_methods_tdf(api_index: models.APIDocIndex, api_processed_terms: set):
    tdf = shared.TERM_DOCUMENT_FREQUENCY
    api_processed_terms = api_processed_terms.copy()
    method_processed_terms = set()
    for methodindex in api_index.methods_index:
        for term in methodindex.text_index.vector:
            if term not in method_processed_terms:
                tdf.add_apimethods_term(term)
                if term not in api_processed_terms:
                    tdf.add_apidm_term(term)
                    api_processed_terms.add(term)
                method_processed_terms.add(term)

        for term in methodindex.code_index.vector:
            if term not in method_processed_terms:
                tdf.add_apimethods_term(term)
                if term not in api_processed_terms:
                    tdf.add_apidm_term(term)
                    api_processed_terms.add(term)


@utils.enforce_types(models.APIDocIndex)
def calculate_api_tdf(api_index: models.APIDocIndex):
    api_processed_terms = set()
    tdf = shared.TERM_DOCUMENT_FREQUENCY
    if not isinstance(tdf, ranking_models.DocumentTermFrequency):
        raise AssertionError("tdf is not an instance of DocumentTermFrequency")

    for term in api_index.text_index.vector:
        if term in api_processed_terms:
            continue
        tdf.add_apidoc_term(term)
        tdf.add_apidm_term(term)

        api_processed_terms.add(term)

    for term in api_index.code_index.vector:
        if term in api_processed_terms:
            continue
        tdf.add_apidoc_term(term)
        tdf.add_apidm_term(term)

        api_processed_terms.add(term)

    calculate_methods_tdf(api_index, api_processed_terms)


def calculate_all_apis_tdf():
    computed = set()

    for apiname in shared.API_SEGMENT_MAP:
        if apiname in computed:
            continue

        seg_id = shared.API_SEGMENT_MAP[apiname]
        seg_apis = pickler.read_api_docs_segment(seg_id)
        for apiname in seg_apis:
            if apiname in computed:
                continue

            calculate_api_tdf(seg_apis[apiname])
            computed.add(apiname)


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
    calculate_all_apis_tdf()

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

    ques_index.title_text_index = combine_title_text_index(ques_index.text_index, ques_index.title_index)
    ques_index.title_text_index.calc_magnitude()

    for ans in question.answers:
        ans_index = models.AnswerIndex(qid=question.id)
        text_index = index_text(ans.text)
        code_index = index_code_snippets(ans.codes)

        ans_index.text.vector = text_index
        ans_index.text.calc_magnitude()

        ans_index.code.vector = code_index
        ans_index.code.calc_magnitude()

        ques_index.answers_index.append(ans_index)

    combined_text = [question.title, question.text]
    for ans in question.answers:
        combined_text.append(ans.text)

    combined_index_vector = index_text("\n".join(combined_text))

    ques_index.full_text_index.vector = combined_index_vector
    ques_index.full_text_index.calc_magnitude()

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

        method_codes = [method.method_name, method.method_sig]
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
    api_index.combined_text_index.calc_magnitude()

    api_index.combined_code_index.vector = api_combined_code_snippets_index
    api_index.combined_code_index.calc_magnitude()

    if api.name.snippet not in shared.API_SEGMENT_MAP:
        shared.TOTAL_API_DOCS += 1
        shared.TOTAL_API_METHODS += len(api.methods)

    return api_index


@utils.enforce_types(models.Index, dict)
def normalize_question_index_with_idf(index: models.Index, idf_vector: dict):
    for term in index.vector:
        if term in idf_vector:
            index.vector[term] *= idf_vector[term]
        else:
            index.vector[term] = 0


@utils.enforce_types(ranking_models.UserQuery, dict)
def index_query(user_query: ranking_models.UserQuery, idf_vector: dict):
    query_index = ranking_models.UserQueryIndex(user_query.id)

    title_iv = index_text(user_query.title)
    text_iv = index_text(user_query.text)
    codes_iv = index_code_snippets(user_query.codes)

    query_index.title_index.vector = title_iv
    normalize_question_index_with_idf(query_index.title_index, idf_vector)
    query_index.title_index.calc_magnitude()

    query_index.text_index.vector = text_iv
    normalize_question_index_with_idf(query_index.text_index, idf_vector)
    query_index.text_index.calc_magnitude()

    query_index.code_index.vector = codes_iv
    normalize_question_index_with_idf(query_index.code_index, idf_vector)
    query_index.code_index.calc_magnitude()

    query_index.title_text_index = combine_title_text_index(query_index.text_index, query_index.title_index)
    query_index.title_text_index.calc_magnitude()

    return query_index


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
