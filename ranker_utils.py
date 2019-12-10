import log
import pickler
import utils
import models, ranking_models
import constants, shared
from copy import deepcopy
import parser
import indexer
import preprocessor


@utils.enforce_types(models.Index, models.Index)
def compute_cosine(index1: models.Index, index2: models.Index):
    shorter_vec = index1 if len(index1) < len(index2) else index2
    longer_vec = index2 if index1 == shorter_vec else index1

    if len(shorter_vec) == 0:
        return 0.0;

    dot_product = 0

    for term in shorter_vec.vector:
        if term in longer_vec.vector:
            dot_product += shorter_vec.vector[term] * longer_vec.vector[term]

    cosine = dot_product / (shorter_vec.magnitude * longer_vec.magnitude)

    return cosine


def combine_index(*args):
    joint_index = deepcopy(args[0])
    for ix in args[1:]:
        if not isinstance(ix, models.Index):
            raise AttributeError("All attributes must be instances of index")

        for term in ix.vector:
            if term not in joint_index.vector:
                joint_index.vector[term] = 0

            joint_index.vector[term] += ix.vector[term]

    return joint_index


@utils.enforce_types(models.APIDocIndex, ranking_models.UserQueryIndex)
def compute_api_cosine(api_index: models.APIDocIndex, queryix: ranking_models.UserQueryIndex):
    q_text_cos = compute_cosine(api_index.text_index, queryix.title_text_index)
    q_code_cos = compute_cosine(api_index.code_index, queryix.code_index)

    return {
        "text_cos": q_text_cos,
        "code_cos": q_code_cos
    }


@utils.enforce_types(ranking_models.UserQueryIndex, models.MethodIndex)
def compute_method_cosine(queryix: ranking_models.UserQueryIndex, method_ix: models.MethodIndex):
    q_text_cos = compute_cosine(queryix.title_text_index, method_ix.text_index)
    q_code_cos = compute_cosine(queryix.code_index, method_ix.code_index)

    return {
        "text_cos": q_text_cos,
        "code_cos": q_code_cos
    }


@utils.enforce_types(models.APIDocIndex, ranking_models.UserQueryIndex)
def compute_all_methods_cosines(api_ix: models.APIDocIndex, queryix: ranking_models.UserQueryIndex):
    methods_index = list()
    for method_ix in api_ix.methods_index:
        methods_index.append(compute_method_cosine(queryix, method_ix))

    return methods_index


@utils.enforce_types(models.APIDocIndex, ranking_models.UserQueryIndex)
def compute_apidm_cosine(api_ix: models.APIDocIndex, queryix: ranking_models.UserQueryIndex):
    q_full_text_cos = compute_cosine(api_ix.combined_text_index, queryix.title_text_index)

    return {
        "full_text_cos": q_full_text_cos
    }


@utils.enforce_types(models.QuestionIndex, ranking_models.UserQueryIndex)
def compute_question_cosine(quesix: models.QuestionIndex, queryix: ranking_models.UserQueryIndex):
    q_text_cos = compute_cosine(quesix.title_text_index, queryix.title_text_index)
    q_code_cos = compute_cosine(quesix.code_index, queryix.code_index)

    return {
        "text_cos": q_text_cos,
        "code_cos": q_code_cos
    }


@utils.enforce_types(ranking_models.UserQueryIndex, models.AnswerIndex)
def compute_answer_cosine(queryix: ranking_models.UserQueryIndex, ansix: models.AnswerIndex):
    q_text_cos = compute_cosine(queryix.title_text_index, ansix.text)
    q_code_cos = compute_cosine(queryix.code_index, ansix.code)

    return {
        "text_cos": q_text_cos,
        "code_cos": q_code_cos
    }


@utils.enforce_types(models.QuestionIndex, ranking_models.UserQueryIndex)
def compute_all_answer_cosines(quesix: models.QuestionIndex, queryix: ranking_models.UserQueryIndex):
    answers_index = list()
    for ansix in quesix.answers_index:
        answers_index.append(compute_answer_cosine(queryix, ansix))

    return answers_index


@utils.enforce_types(models.QuestionIndex, ranking_models.UserQueryIndex)
def compute_qa_cosine(quesix: models.QuestionIndex, queryix: ranking_models.UserQueryIndex):
    q_full_text_cos = compute_cosine(quesix.full_text_index, queryix.title_text_index)

    return {
        "full_text_cos": q_full_text_cos
    }


if __name__ == "__main__":
    from starter import init, end

    init()
    qindex = dict()
    to_process = ["15235400", "15796781"]
    for qid in to_process:
        fname = f"dataset/questions/raw/{qid}.html"
        q = parser.parse_question_from_file(fname)
        qindex[q.id] = indexer.index_question(q)

    # pickler.write_questions_index(qindex)
    # indexer.calculate_all_idf()

    newq = "6619516"
    fname = f"dataset/questions/raw/{newq}.html"
    q = parser.parse_question_from_file(fname)
    query = ranking_models.UserQuery(title=q.title, text=q.text, code_snippets=[c.snippet for c in q.codes], tags=[])
    newqindex = indexer.index_query(query)

    log.debug(f"For question {to_process[0]}")

    qcosine = compute_question_cosine(qindex["15235400"], newqindex)
    qacosine = compute_qa_cosine(qindex["15235400"], newqindex)
    answer_cosines = list()
    for ansix in qindex["15235400"].answers_index:
        answer_cosines.append(compute_answer_cosine(newqindex, ansix))

    end()
