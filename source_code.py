from lxml import etree as ET
import copy
import gdown
import openai
import json

def download_doc():
    # url = 'https://docs.google.com/document/d/1qjU6jTGc0S15Q2uKqg9xzU4aEZwiSy3JdIHWwesacAg/edit#heading=h.9lzfy7qipbhf'
    url = input("Please enter the url of the google doc - ").strip()
    output = './info/questions.txt'
    gdown.download(url, output, quiet=False, fuzzy=True, format='txt')

def read_questions():
    with open('./info/questions.txt','r', encoding='utf-8-sig') as f:
        try:
            raw_data = f.read()
            quiz = json.loads(raw_data)
        except json.decoder.JSONDecodeError as error:
            error_pos = error.pos
            print(f"Format found wrong at position {error_pos}")
            print(f"Errored Character - '{raw_data[error_pos]}'")
            print(f"Which is around :-")
            input(raw_data[error_pos-15:error_pos+15])
            quit()

    return quiz


def check_format(quiz):
    if 'title' not in quiz:
        input("\nTitle not found.")
        quit()

    if "questions" in quiz:
        print(f"Found a total of {len(quiz['questions'])} questions.")

        for i, qn in enumerate(quiz['questions']):
            if 'question' not in qn:
                input(f'question not found in - \n{qn}')
            elif not isinstance(qn['question'],str):
                input(f'question is not in the right format in - \n{qn}')

            
            if 'explanation' not in qn:
                input(f'explanation not found in - \n{qn}')
            elif not isinstance(qn['explanation'],str):
                input(f'explanation is not in the right format in - \n{qn}')

            if 'hint' not in qn:
                input(f'hint not found in - \n{qn}')
            elif not isinstance(qn['hint'],str):
                input(f'hint is not in the right format in - \n{qn}')

            if 'option1' not in qn:
                input(f'options are not named properly in - \n{qn}')

            for key in qn:
                if 'option' in key:
                    if not isinstance(qn[key],str):
                        input(f'option is not in the right format in - \n{qn}')

            if 'answers' not in qn:
                input(f'answers not found in - \n{qn}')
            elif not isinstance(qn['answers'],list):
                input(f'answers is not in the right format in - \n{qn}')
            else:
                if len(qn['answers']) < 1:
                        input(f"No answers given in - \n{qn}")
                else:
                    for ans_option in qn['answers']:

                        if not isinstance(ans_option,str):
                            input(f"{ans_option} is not a valid answer in - \n{qn}")

                        elif ans_option not in qn or not isinstance(qn[ans_option],str):
                            input(f"{ans_option} is not a valid answer in - \n{qn}")


        mykeys = {'question':[],'answers':[],'explanation':[],'hint':[]}
        for qn in quiz['questions']:
            for key in mykeys:
                if qn[key] in mykeys[key]:
                    input(f"Duplicate {key} found in - \n{qn}")
                    quit()



def prep_xml(quiz):
    parser = ET.XMLParser(strip_cdata=False)

    tree = ET.parse('./info/ref_structure.xml',parser) 

    root = tree.getroot() 

    root.find('.//title').text = ET.CDATA(quiz['title'])

    qns_element = root.find(".//questions")
    qn_element = root.find(".//questions/question")

    new_qns = quiz['questions']

    for i in range(len(new_qns)-1):
        qns_element.append(copy.deepcopy(qn_element))

    question_elems = root.findall(".//questions/question")
    for qn_counter, qn in enumerate(new_qns):
        question_elem = question_elems[qn_counter]

        # if len(qn['answers']) > 1:
        if 'select all that apply' in qn['question'].lower():
            question_elem.set('answerType','multiple')
        else:
            question_elem.set('answerType','single')


        question_elem.find('title').text = ET.CDATA(f"Question: {qn_counter+1}")
        question_elem.find('questionText').text = ET.CDATA(f"<h4>{qn['question']}</h4>")
        question_elem.find('correctMsg').text = ET.CDATA(qn['explanation'])
        question_elem.find('tipMsg').text = ET.CDATA(qn['hint'])

        # answer_elems = question_elem.findall('./answers/answer')
        answers_elem = question_elem.find('./answers')
        answer_elem = question_elem.find('./answers/answer')

        answers_elem.remove(answer_elem)

        for key in qn:
            if 'option' in key:

                if key in qn['answers']:
                    answer_elem.set('correct','true')
                else:
                    answer_elem.set('correct','false')

                answer_elem.find('./answerText').text = ET.CDATA(qn[key])

                answers_elem.append(copy.deepcopy(answer_elem))


    tree.write(f'{quiz["title"]}.xml', xml_declaration=True)
        
    
    
download_doc()
 
quiz = read_questions()

check_format(quiz)

prep_xml(quiz)
    