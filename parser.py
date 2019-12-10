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
        log.log(f" Failed to find upvote count", module="parser")

    outlinks_soup = answer_content_soup.findAll('a', href=True)
    outlinks = [a['href'] for a in outlinks_soup]

    [ol.replaceWith('') for ol in outlinks_soup]
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

def parse_API_doc(doc_soup: BeautifulSoup):

    class_name = doc_soup.find('h2',attrs={'class':'title'}).text
    # print(class_name)
    module_div = doc_soup.find('span',attrs={'class':'moduleLabelInType'}).parent
    module_name = module_div.find('a').text
    # print("Module name "+str(module_name))

    package_div = doc_soup.find('span',attrs={'class':'packageLabelInType'}).parent
    package_name = package_div.find('a').text
    # print("Package" + str(package_name))

    description_div = doc_soup.find('div',attrs={'class':'description'})
    method_signature = description_div.find('pre').text
    # print("method signature" + str(method_signature))

    description = description_div.find('div',attrs={'class':'block'}).text
    # print("Description" + str(description))

    apiDocObject = models.APIDoc(name=class_name, module=module_name, package=package_name, doc_text=description,
                                code_snippets=[method_signature], lang="java")

    # if(doc_soup.find('a',attrs={'id':'field.summary'})):
    #     fields_table = doc_soup.find('a',attrs={'id':'field.summary'}).parent.findAll('tr')[1:]
    #     for row in fields_table:
    #         fieldname = row.find('td',attrs={'class':'colFirst'}).text
    #         field_sig = row.find('th',attrs={'class':'colSecond'}).text
    #         desc = row.find('td',attrs={'class':'colLast'}).text
    #
    #         print(fieldname)
    #         apiDocObject.add_field(field_name=fieldname, field_signature=field_sig, description=desc)


    # if(doc_soup.find('a',attrs={'id':'method.summary'})):
    #     methods_table = doc_soup.find('a',attrs={'id':'method.summary'}).parent.findAll('tr')[1:]
    #     print(len(methods_table))
    #     for row in methods_table:
    #         # print(row)
    #         method_name = row.find('td',attrs={'class':'colFirst'}).text
    #         method_sig = row.find('th',attrs={'class':'colSecond'}).text
    #         desc = row.find('td',attrs={'class':'colLast'}).text
    #
    #         print(method_sig)
    #         apiDocObject.add_method(method_name=method_name, method_signature=method_sig, description=desc)

    if(doc_soup.find('a',attrs={'id':'method.detail'})):
        # print('Fetching method details')
        method_details = doc_soup.find('a',attrs={'id':'method.detail'}).parent.findAll('ul',attrs={'class':'blockList'})
        # print(method_details)
        for row in method_details:
            # print(row)
            method_name = row.find('h4').text
            method_sig = row.find('pre',attrs={'class':'methodSignature'}).text
            desc = row.find('div',attrs={'class':'block'}).text
            # print(method_sig)
            apiDocObject.add_method(method_name=method_name, method_signature=method_sig, description=desc)

        last_detail = doc_soup.find('a',attrs={'id':'method.detail'}).parent.find('ul',attrs={'class':'blockListLast'})
        # print(last_detail)
        method_name = last_detail.find('h4').text
        method_sig = last_detail.find('pre',attrs={'class':'methodSignature'}).text
        desc = last_detail.find('div',attrs={'class':'block'}).text
        # print(method_sig)
        apiDocObject.add_method(method_name=method_name, method_signature=method_sig, description=desc)

    print('\n---------')

    if(doc_soup.find('a',attrs={'id':'field.detail'})):
        # print('Fetching field details')
        field_details = doc_soup.find('a',attrs={'id':'field.detail'}).parent.findAll('ul',attrs={'class':'blockList'})
        # print(method_details)
        for row in field_details:
            # print(row)
            field_name = row.find('h4').text
            field_sig = row.find('pre').text
            desc = row.find('div',attrs={'class':'block'}).text
            apiDocObject.add_field(field_name=field_name, field_signature=field_sig, description=desc)
            # print(field_sig)

        last_detail = doc_soup.find('a',attrs={'id':'field.detail'}).parent.find('ul',attrs={'class':'blockListLast'})
        # print(last_detail)
        field_name = last_detail.find('h4').text
        field_sig = last_detail.find('pre').text
        desc = last_detail.find('div',attrs={'class':'block'}).text
        # print(field_sig)
        # print(desc)
        apiDocObject.add_field(field_name=field_name, field_signature=field_sig, description=desc)
    #

    return apiDocObject



def parse_question_from_file(file):
    f = open(file, mode="r")
    q2_raw = f.read()
    f.close()

    soup2 = BeautifulSoup(q2_raw, 'html.parser')

    question = parse_question(soup2)

    log.success(f" question {question.id} parsed", module="parser")
    return question

def parse_API_doc_driver(file):
    f = open(file,mode='r')
    doc_raw = f.read()
    f.close()

    soupObject = BeautifulSoup(doc_raw,'html.parser')
    parsedDoc = parse_API_doc(soupObject)
    # print('Checking in parser.')

    # print(parsedDoc.methods)
    # for method in parsedDoc.methods:
        # print(method.method_sig.snippet)
    # print(new_doc.text)
    # print('\n\n\n\n\n\n\n\n')
    # print(parsedDoc.__dict__)
    jsonified = parsedDoc.to_json()
    # obj = models.APIDoc.from_json(jsonified)
    # print(obj.__dict__)

    log.success(f" Document {parsedDoc.name} parsed", module="parser")
    return jsonified

def test_method():

    method = models.APIField('testname','testsignature','testdesc')
    print(method.__dict__)
    jsonified = method.to_json()
    obj = models.APIField.from_json(jsonified)
    print(obj.__dict__)

if __name__ == "__main__":
    file = "dataset/questions/raw/using-filechannel-to-write-any-inputstream?.html"
    # q = parse_question_from_file(file)
    parse_API_doc_driver('dataset/API/raw/docs/api/java.compiler/javax/annotation/processing/AbstractProcessor.html')

    # print(q.to_json())

    # test_method()
