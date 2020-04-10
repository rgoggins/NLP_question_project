
'''
@file answer.py
@brief A python script for generating answers to a series of questions
11-411: Natural Language Processing
@author Ryan Goggins <goggins@cmu.edu>
@author Casey Al-Haddad <chaddad@andrew.cmu.edu>
@author Justin Lee <justinl2@andrew.cmu.edu>
@author Oliver Pennington <oop@cmu.edu>
'''
# from tokenizer import *
import nltk
nltk.download("punkt", quiet = True)
nltk.download("averaged_perceptron_tagger", quiet = True)
#from edit_dist import *
from spacy import load
from tokenizer import *
from textblob import Word
from textblob import TextBlob
nlp = load("en_core_web_md")

class Answer:
    def __init__(self, textfile):
        #TODO process corpus based on tokenization
        # f = open(textfile, "r+")
        # corpus = f.read()
        corpus = textfile
        self.corpus = corpus
        self.tb = TextBlob(corpus)
        self.NLP = nlp(corpus)
    def get_relevant_sentences(self, question):
        a = set(TextBlob(question).words)
        snts = self.tb.sentences
        return sorted(snts, key = lambda sent: len(a - set(sent.words)))

    def get_relevant_sentence(self, question):
        most_relevant = None
        lowest_edit_dist = float('inf')

        a = set(TextBlob(question).words)
        for sent in self.tb.sentences:
            sentstr = str(sent)
            b = set(sent.words)
            missing = a - b
            # levenshtein = calculateLevenshteinDistance(question, sentstr)
            levenshtein = len(missing)
            if (levenshtein < lowest_edit_dist):
                lowest_edit_dist = levenshtein
                most_relevant = sent

        return most_relevant

    #NOTE: final version will only have self and question parameter.
    def answer_question(self, question):
        #tokenize question
        tk = TextBlob(question)
        qcorpus = nlp(question)
        #get sentence most relevant to the question
        relevant_sentence = str(self.get_relevant_sentence(question))

        #WHICH?????
        PERSON_QUESTION = "PERSON"
        YES_NO_QUESTION = "YN"
        PLACE_QUESTION = "PLACE"
        TIME_QUESTION = "TIME"
        OBJECT_QUESTION = "OBJECT"

        person_words = ["who", "whom"]
        place_words = ["where"]
        time_words = ["when"]
        object_words = ["what", "which"]
        yes_no_words = set(["is", "does", "are", "was", "were", "did", "has", "could", "will", "have","can"])

        person_tags = ["PERSON"]
        place_tags = ["GPE", "LOC"]
        object_tags = ["ORG", "GPE", "LOC"]
        qType = None
        for w in qcorpus:
            word = w.text.lower()
            if word in person_words:
                qType = PERSON_QUESTION
                break
            if word in place_words:
                qType = PLACE_QUESTION
                break
            if word in time_words:
                qType = TIME_QUESTION
                break
            if word in yes_no_words:
                qType = YES_NO_QUESTION
                break
            if word in object_words:
                qType = OBJECT_QUESTION
                break
        # selected_passage_ents = nlp(relevant_sentence).ents
        # for entity in selected_passage_ents:
        #     print(entity.text, entity.label_)
        #Split into types of questions:
        #PERSON: (WHO)
        spes = self.get_relevant_sentences(question)
        for sp in spes:
            selected_passage_ents = nlp(str(sp)).ents
            if qType is PERSON_QUESTION:
                for entity in selected_passage_ents:
                    if entity.label_ in person_tags:
                        return entity.text
                #DO PERSON CASE
                # return "COULD NOT FIND PERSON"

            #PLACE: (WHERE)
            elif qType is PLACE_QUESTION:
                for entity in selected_passage_ents:
                    if entity.label_ in place_tags:
                        return entity.text
                # for entity in selected_passage_ents:
                #     print(entity.text, entity.label_)
                # return "COULD NOT FIND PLACE"

            #TIME: (WHEN)
            elif qType is TIME_QUESTION:
                #NOTE: this is a little buggy, we may want to manually search for dates
                for entity in selected_passage_ents:
                    if entity.label_ in ["DATE"]:
                        return entity.text
                for entity in selected_passage_ents:
                    if entity.label_ in ["CARDINAL"]:
                        return entity.text
                # return "COULD NOT FIND TIME"

            #YES/NO QUESTION
            elif qType is YES_NO_QUESTION:
                q_tags = tk.tags
                keyword = ""
                key_tag = ""
                for (token, tag) in q_tags:
                    if tag[0] == 'N' or tag[0] == "V":
                        keyword = token
                        key_tag = tag

                keyword_found = False
                neg = False
                for token in nlp(relevant_sentence):
                    if str(token) == keyword or (key_tag[0] == "V" and Word(str(token)).lemmatize("v") == Word(keyword).lemmatize("v")):
                        keyword_found = True
                    if token.dep_ == 'neg':
                        neg = not neg

                if keyword_found:
                    if neg: return "No"
                    else: return "Yes"
                return "No"

            #REASON (WHY)
            #NOTE: Probably don't have to do this, oddball questins
            else:
                #DO THIS CASE
                # return "COULD NOT FIND REASON"
                pass

        for sp in spes:
            selected_passage_ents = nlp(str(sp)).ents
            for entity in selected_passage_ents:
                return entity.text
        return "Unsure"


def test():
    #WHERE
    q1_corpus = "Chipata Mountain is a mountain in central Malawi. It is located in Nkhotakota District, north of the town of Mbobo. Chipata Mountain is in Nkhotakota Wildlife Reserve, and is the reserve's tallest peak. It is located at the park's western edge. The wildlife refuge lies on the western edge of the East African Rift, and Chipata Mountain is part of a north-south belt of hills, mountains, and escarpments that form the western boundary of the rift. To the east is a plain that borders on Lake Malawi. To the west is the Central Region Plateau, also known as the Lilongwe Plain."
    q1_most_relevant_sentence = "Chipata Mountain is in Nkhotakota Wildlife Reserve"
    q1_answerer = Answer(q1_corpus)
    q1_question = "Where is Chiapata Mountain?"
    q1_ans = q1_answerer.answer_question(q1_question)
    print("Q1 Question: \"",q1_question,"\"", sep = "")
    print("Q1 Answer:   \"",q1_ans,"\"", sep = "")
    print("---------------------")

    # YES/NO
    q2_corpus = "Up is not down. The sky is not red. The sky is blue."
    q2_most_relevant_sentence = "The sky is not red."
    q2_answerer = Answer(q2_corpus)
    q2_question = "Is the sky red"
    q2_ans = q2_answerer.answer_question(q2_question)
    print("Q2 Question: \"", q2_question, "\"", sep = "")
    print("Q2 Answer:   \"", q2_ans, "\"", sep = "")
    print("Q2 Solution: \"No\"")
    print("---------------------")

    q3_long_corpus = """
    Sigma Octantis is the closest naked-eye star to the south Celestial pole, but at apparent magnitude 5.45 it is barely visible on a clear night, making it unusable for navigational purposes. It is a yellow giant 275 light years from Earth. Its angular separation from the pole is about 1° (as of 2000). The Southern Cross constellation functions as an approximate southern pole constellation, by pointing to where a southern pole star would be.
At the equator, it is possible to see both Polaris and the Southern Cross.  The Celestial south pole is moving toward the Southern Cross, which has pointed to the south pole for the last 2000 years or so. As a consequence, the constellation is no longer visible from subtropical northern latitudes, as it was in the time of the ancient Greeks.
Around 200 BC, the star Beta Hydri was the nearest bright star to the Celestial south pole. Around 2800 BC, Achernar was only 8 degrees from the south pole.
In the next 7500 years, the south Celestial pole will pass close to the stars Gamma Chamaeleontis (4200 AD), I Carinae, Omega Carinae (5800 AD), Upsilon Carinae, Iota Carinae (Aspidiske, 8100 AD) and Delta Velorum (9200 AD). From the eightieth to the ninetieth centuries, the south Celestial pole will travel through the False Cross. Around 14,000 AD, when Vega is only 4° from the North Pole, Canopus will be only 8° from the South Pole and thus circumpolar on the latitude of Bali (8°S).
Sirius will take its turn as the South Pole Star in the year 66,270 AD. In fact, Sirius will come to within 1.6 degree of the south celestial pole in 66,270 AD. Later, in the year 93,830 AD, Sirius will miss aligning with the south celestial pole by only 2.3 degree."
"""
    q3_most_relevant_sentence = "Sigma Octantis is the closest naked-eye star to the south Celestial pole, but at apparent magnitude 5.45 it is barely visible on a clear night, making it unusable for navigational purposes"
    q3_answerer = Answer(q3_long_corpus)
    q3_question = "Where is Sigma Octantis close to?"
    q3_ans = q3_answerer.answer_question(q3_question)
    print("Q3 Question: \"", q3_question, "\"", sep = "")
    print("Q3 Answer:   \"", q3_ans, "\"", sep = "")
    print("Q3 Solution: \"the south Celestial pole\"")
    print("---------------------")

    q4_corpus = "Around 200 BC, the star Beta Hydri was the nearest bright star to the Celestial south pole. Around 2800 BC, Achernar was only 8 degrees from the south pole."
    q4_answerer = Answer(q4_corpus)
    q4_question1 = "When was Beta Hydri the nearest bright star to the Celestial south pole?"
    q4_most_relevant_sentence1 = "Around 200 BC, the star Beta Hydri was the nearest bright star to the Celestial south pole."
    q4_ans1 = q4_answerer.answer_question(q4_question1)
    print("Q4 Question 1: \"", q4_question1, "\"", sep = "")
    print("Q4 Answer 1:   \"", q4_ans1, "\"", sep = "")
    print("Q4 Solution 1: \"200 BC\"")
    print("---------------------")
    #NOTE: Most relevant sentence isn't being taken into consideration which is why this doesnt work
    q4_question2 = "When was Achernar only 8 degrees from the south pole?"
    q4_most_relevant_sentence2 = "Around 2800 BC, Achernar was only 8 degrees from the south pole."
    q4_ans2 = q4_answerer.answer_question(q4_question2)
    print("Q4 Question 2: \"", q4_question2, "\"", sep = "")
    print("Q4 Answer 2:   \"", q4_ans2, "\"", sep = "")
    print("Q4 Solution 2: \"2800 BC\"")
    print("---------------------")

    q5_corpus = "Kobe played basketball everyday. He never played soccer."
    q5_most_relevant_sentence = "Kobe played basketball everyday"
    q5_answerer = Answer(q5_corpus)
    q5_question = "Did Kobe play basketball?"
    q5_ans = q5_answerer.answer_question(q5_question)
    print("Q5 Question: \"", q5_question, "\"", sep="")
    print("Q5 Answer:   \"", q5_ans, "\"", sep="")
    print("Q5 Solution: \"Yes\"")
    print("---------------------")
def test_file():
    pass
if __name__ == "__main__":
    test()
