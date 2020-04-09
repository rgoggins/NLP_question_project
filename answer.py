'''
@file answer.py
@brief A python script for generating answers to a series of questions

11-411: Natural Language Processing

@author Ryan Goggins <goggins@cmu.edu>
@author Casey Al-Haddad <chaddad@andrew.cmu.edu>
@author Justin Lee <justinl2@andrew.cmu.edu>
@author Oliver Pennington <oop@cmu.edu>

'''
from tokenizer import *
import spacy
model = spacy.load("en_core_web_md")

class Answer:
    def __init__(self, corpus):
        #TODO process corpus based on tokenization
        self.corpus = corpus

    #NOTE: final version will only have self and question parameter.
    def answer_question(self, question, most_relevant_sentence):
        #tokenize question
        tk = TextBlob(question)

        #get sentence most relevant to the question
        relevant_sentence = most_relevant_sentence

        first_question_word = question.split(" ")[0]
        #Split into types of questions:
        person_words = ["Who", "Whom"]
        #PERSON: (WHO)
        if first_question_word in person_words:
            pass
            #DO PERSON CASE
            return "PERSON"

        #PLACE: (WHERE)
        place_words = ["Where"]
        if first_question_word in place_words:
            pass
            #DO PLACE CASE
            return "PLACE"

        #TIME: (WHEN)
        time_words = ["When"]
        if first_question_word in time_words:
            pass
            #DO TIME CASE
            return "TIME"

        #YES/NO QUESTION
        yes_no_words = ["Is", "Does", "Are", "Was", "Were", "Did", "Has", "Could", "Will", "Have"]
        if first_question_word in yes_no_words:
            q_tags = tk.pos_tags
            keyword = ""
            for (token, tag) in q_tags:
                if tag == 'NN' or tag == 'NNS' or tag == 'NNP' or tag == "NNPS":
                    keyword = token
            if keyword in relevant_sentence:
                prev = ""
                # assumes that relevant_sentence is a string
                for token in model(relevant_sentence):
                    if str(token) == str(keyword):
                        if prev == 'neg':
                            return "No"
                        else:
                            return "Yes"
                    if token.dep_ == 'neg':
                        prev = 'neg'
                    else:
                        prev = ""
            else:
                return "No"

        #REASON (WHY)
        #NOTE: Probably don't have to do this, oddball questins
        why_words = ["Why"]
        if first_question_word in why_words:
            pass
            #DO THIS CASE
            return "reason"

        return "Unsure"


def test():
    #WHERE
    q1_corpus = "Chipata Mountain is a mountain in central Malawi. It is located in Nkhotakota District, north of the town of Mbobo. Chipata Mountain is in Nkhotakota Wildlife Reserve, and is the reserve's tallest peak. It is located at the park's western edge. The wildlife refuge lies on the western edge of the East African Rift, and Chipata Mountain is part of a north-south belt of hills, mountains, and escarpments that form the western boundary of the rift. To the east is a plain that borders on Lake Malawi. To the west is the Central Region Plateau, also known as the Lilongwe Plain."
    q1_most_relevant_sentence = "Chipata Mountain is in Nkhotakota Wildlife Reserve"
    q1_answerer = Answer(q1_corpus)
    q1_question = "Where is Chiapata Mountain?"
    q1_ans = q1_answerer.answer_question(q1_question, q1_most_relevant_sentence)
    print("Q1 Question: \"",q1_question,"\"", sep = "")
    print("Q1 Answer:   \"",q1_ans,"\"", sep = "")
    print("---------------------")

    # YES/NO
    q2_corpus = "Up is not down. The sky is not red. The sky is blue."
    q2_most_relevant_sentence = "The sky is blue."
    q2_answerer = Answer(q2_corpus)
    q2_question = "Is the sky blue?"
    q2_ans = q2_answerer.answer_question(q2_question, q2_most_relevant_sentence)
    print("Q2 Question: \"", q2_question, "\"", sep = "")
    print("Q2 Answer:   \"", q2_ans, "\"", sep = "")
    print("---------------------")


if __name__ == "__main__":
    test()
