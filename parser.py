from bs4 import BeautifulSoup

import log
import models
import utils


def parse_answer(answer_soup: BeautifulSoup):
    answer_content_soup = answer_soup.find('div', attrs={'class': 'post-text'})
    answer_upvote_count_soup = answer_soup.find('div', attrs={'itemprop': 'upvoteCount'})
    upvotes = 0
    if answer_upvote_count_soup:
        upvotes = int(answer_upvote_count_soup['data-value'])
    else:
        log.log("parser", f" Failed to find upvote count")

    outlinks_soup = answer_content_soup.findAll('a', href=True)
    outlinks = [a['href'] for a in outlinks_soup]

    code_snippets_soups = answer_content_soup.findAll('code')
    code_snippets_texts = [code.text for code in code_snippets_soups]

    # remove all code tags from text
    [code_soup.replaceWith('') for code_soup in code_snippets_soups]

    answer_text_content = answer_content_soup.text
    answer_object = models.Answer(url="", text=answer_text_content, code_snippets=code_snippets_texts,
                                  out_links=outlinks, upvotes=upvotes, lang="java")

    return answer_object


def parse_question(page_soup: BeautifulSoup):
    qtitle = page_soup.find('title').text
    question_block = page_soup.find('div', attrs={'class': 'question'})
    question_id = question_block['data-questionid']
    question_content_soup = question_block.find('div', attrs={'class': 'post-text'})
    # print(qcontent)

    question_code_snippets = question_content_soup.findAll('code')
    question_code_snippets_text = [code.text for code in question_code_snippets]

    # remove all code tags from text
    [qct.replaceWith('') for qct in question_code_snippets]

    outlinks_soups = question_content_soup.findAll('a', href=True)
    outlinks = [a['href'] for a in outlinks_soups]

    question_text = question_content_soup.text  # this text wont contain code blocks

    answer_soups = page_soup.findAll('div', attrs={'class': 'answer'})
    answers = [parse_answer(ans) for ans in answer_soups]
    answers.sort(key=lambda a: a.upvotes, reverse=True)

    question_object = models.Question(url="", title=qtitle, question_id=question_id, text=question_text,
                                      code_snippets=question_code_snippets_text,
                                      out_links=outlinks, answers=answers, lang="java")

    return question_object


def parse_question_from_file(file):
    f = open(file, mode="r")
    q2_raw = f.read()
    f.close()

    soup2 = BeautifulSoup(q2_raw, 'html.parser')

    question = parse_question(soup2)

    log.success("parser", f" question {question.id} parsed")
    return question


if __name__ == "__main__":
    file = "dataset/questions/raw/using-filechannel-to-write-any-inputstream?.html"
    q = parse_question_from_file(file)
    print(q.to_json())