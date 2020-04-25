#!/usr/bin/python
'''
@file ask.py
@brief A python script for generating questions about a given document

11-411: Natural Language Processing

@author Ryan Goggins <goggins@cmu.edu>
@author Casey Al-Haddad <chaddad@andrew.cmu.edu>
@author Justin Lee <justinl2@andrew.cmu.edu>
@author Oliver Pennington <oop@cmu.edu>

'''
import os
import re
import math
import spacy
import sys
import random
from tokenizer import *
import nltk
from textblob import TextBlob
nlp = spacy.load('en_core_web_md')


# Passed in documents and a number 'n' of questions we are required to generate
# Load in the tokenized data
# Create NER table
# Find most frequent entities referenced by document
# Split up questions equally into Who? What? Is/was? (only binary questions for now)
# A question should have its answer in a single sentence

tokenized_data = None # call whatever tokenizer.py function gets the data
num_questions = 10 # this is also passed in

# sentiment_q = False

def check_question_grammar(question):
    pass


def generate_where_question(root_sentence):
    # These are too arbitrary, too difficult to determine locations
    pass


def generate_when_question(root_sentence):
    # Find the date
    # can I just replace it with March 10 of what year
    # Replace month, year,

    year = None
    ind = -1

    sentencestr = str(root_sentence).split()
    # sentencestr = "Northward, in the 2nd century AD, the Kushans under Kanishka made various forays into the Tarim Basin, where they had various contacts with the Chinese.".split()
    newsent = []
    # print("Sentence: " + str(sentencestr))

    altered = False

    for i, word in enumerate(sentencestr):
        # print("Iteration " + str(i) + ": " + word)
        if (len(word) == 4 and word.isdigit() and (word[:2] in ["18", "19", "20"])):
            year = int(word)
            ind = i
            # replace it
            # print("Previous: " + str(sentencestr[i-1]))
            if (i > 0) and (i < len(root_sentence.words) - 1):
                if (sen.tags[i-1][1] == "NN") and (sen.tags[i+1][1] == "NN"):
                    continue

            if (i > 0) and (sentencestr[i-1].lower() == "the"):
                newsent = newsent[:-1]
                newsent.append("which year of the")
                altered = True
                continue
            if (i > 0) and (sentencestr[i-1].lower() in ["in", "on", "between"]):
                newsent.append("what year")
                altered = True

                continue
            else:
                altered = True
                newsent.append("in which year")
                continue
        elif (word.isdigit() and (i < len(sentencestr) - 1) and sentencestr[i+1] in ["BC", "AD", "BCE"]):
            # This is a date
            altered = True
            newsent.append("in about which year")

        elif ((word[0].isdigit()) and (not word[-1].isdigit()) and (i < len(sentencestr) - 2) and (sentencestr[i+1] == "century") and (sentencestr[i+2][:2] in ["BC", "AD", "CE"])):
            altered = True
            newsent.append("which")
        else:
            newsent.append(word)

    if (not altered):
        return None

    return " ".join(newsent)[:-1] + "?"


def generate_who_question(root_sentence, man, woman, entity):
    # Find the noun phrase with an NER about a person in it
    topic = None
    chunk = None
    sentencestr = str(root_sentence)
    for s in nltk.sent_tokenize(sentencestr):
        for ch in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(s))):
            if hasattr(ch, 'label'):
                # print("label: " + str(ch.label()))
                if (ch.label() == "PERSON"):
                    chunk = ch
                    topic = " ".join(c[0] for c in ch)
                    break
    if (topic == None):
        # print("No PERSON found in the sentence: " + sentencestr)
        return None


    # print("topic: " + str(topic) + " end")

    first = True

    def name_replacement(m):
        value = m.group(0)

        # print("Here is the value we are replacing:" + str(value) + "END.")
        if (first):
            if (str(value) == topic):
                # Replace with 'who'
                if (man or woman):
                    return "who"
                return "what"
            else:
                # Replace with he or his (appropriate pronoun)
                if (man or woman):
                    return "who"
                return "what"
        else:
            if (man):
                return "he"
            elif (woman):
                return "she"
            return "it"
            # Replace with pronoun

    fn_string = "(?<![-\w\d])(" + str(topic) + "|"

    if (len(chunk) > 0):
        for name in chunk:
            fn_string += str(name) + "|"
    fn_string = fn_string[:-1] + ")"

    # print("Original sentence: " + str(sentencestr))

    altered = re.sub(fn_string, name_replacement, sentencestr)
    # print("Altered: " + str(altered))
    altered = altered[0].upper() + altered[1:-1] + "?"

    return altered

def gen_when(f):
    le = set([(x.text.strip()) for x in list(nlp(f).ents) if str(x.label_) in ["DATE","TIME"]])
    qcands = []
    for sent in TextBlob(f).sentences:
        ssent = str(sent).strip().replace(".", "")
        keywords = ["on", "in", "during"]
        is_cand = any([ssent.lower().find(keyword) == 0 for keyword in keywords])
        if is_cand:
            wo_first = ssent[ssent.find(" "):].strip()
            for t in le:
                woi = wo_first.find(t)
                ssi = ssent.find(t)
                if woi == 0:
                    sent_stub = wo_first[len(t) + 1:].strip()
                    first_word = sent_stub.split(" ")[0].lower()
                    if not first_word in ["he", "she", "it", "they"]: #avoid ambiguity
                        if not first_word.replace(",", "").isnumeric(): #avoid misparse
                            s_formed = ("When is it that " + sent_stub + "?")
                            qcands.append(s_formed)
                            break
                if ssi == 0:
                    sent_stub = ssent[len(t) + 1:].strip()
                    first_word = sent_stub.split(" ")[0].lower()
                    if not first_word in ["he", "she", "it", "they"]: #avoid ambiguity
                        if not first_word.replace(",", "").isnumeric():
                            s_formed = ("When is it that " + sent_stub + "?")
                            qcands.append(s_formed)
                            break
    return qcands

def generate_binary_question(root_sentence):
    phrase = "Is it correct that "
    if (random.randint(1,2) == 1):
        phrase = "Is it true that "
    sent_frag = str(root_sentence)

    def fn_replacement(m):
        value = m.group(0)
        # print("Value is " + str(value))
        if (random.randint(1,2) == 1):
            number = int(value)
            if (abs(number - 1990) < 30):
                return " " + str(random.randint(1,30) + 1990) + ""
            return " " + str(number*2) + ""
        else:
            return str(value)
    match = '\s\d\d*'
    sent_frag = re.sub(match, fn_replacement, str(root_sentence))
    word1 = root_sentence.tags[0]
    if (word1[1] != "NNP"):
        # print("First word is not a proper noun " + str(word1[0]))
        sent_frag = sent_frag[0].lower() + "" + sent_frag[1:]
    sent_frag = sent_frag[:-1] + "?"
    return phrase + sent_frag

invalid_starting_labels = ["PRP", "PRP$", "DT"]

def meets_binary_crit(sentence, iter):
    return (len(sentence.words) > 15 - iter) and ('\n' not in str(sentence)) and (sen.tags[0][1] not in invalid_starting_labels) and (abs(sen.sentiment.polarity) >0.4 - float(iter)/10.0) and ('"' not in str(sentence)) and ("for example" not in str(sentence).lower())

def meets_who_crit(sentence, iter):
    return ('\n' not in str(sentence)) and (sen.tags[0][1] not in invalid_starting_labels) and (abs(sen.sentiment.polarity) >0.3 - float(iter)/10.0) and (len(sentence.words) > 10) and ('"' not in str(sentence)) and ("for example" not in str(sentence).lower())

def meets_when_crit(sentence, iter):
    return (len(sentence.words) > 15 - iter) and ('\n' not in str(sentence)) and (sen.tags[0][1] not in invalid_starting_labels) and ('"' not in str(sentence)) and ("for example" not in str(sentence).lower())


def subject_not_preposition(sentence):
    st = str(sentence)
    doc = nlp(st)
    subjects = [str(x) for x in doc if (x.dep_ == "nsubj")]
    if (len(subjects) == 0):
        return False

    sub = subjects[0]
    newtk = TextBlob(sub)
    if (newtk.tags[0][1] == "PRP"):
        return False
    return True

if __name__ == "__main__":


    questions = []

    sentence_roots = []
    filename = str(sys.argv[1])
    num_questions = int(sys.argv[2])

    man = False
    woman = False
    entity = False

    it_count = 0
    he_count = 0
    she_count = 0

    tk = Tokenizer(filename)

    for sentence in tk.blob.sentences:
        for word in sentence.words:
            if (str(word).lower() == "it"):
                it_count += 1
            elif (str(word).lower() == "he"):
                he_count += 1
            elif (str(word).lower() == "she"):
                she_count += 1

    if (max(it_count, he_count, she_count) == it_count):
        entity = True
    elif (max(it_count, he_count, she_count) == he_count):
        man = True
    else:
        woman = True

    when_questions = gen_when(str(tk.blob))

    index = 0
    turn = 0

    while (len(questions) < num_questions):
        iter = (index // len(tk.blob.sentences))
        sen = tk.blob.sentences[index % len(tk.blob.sentences)]
        if (sen not in sentence_roots) and (subject_not_preposition(sen)):
            if (turn % 3 == 0):
                if (meets_binary_crit(sen, iter)):
                    output = generate_binary_question(sen)
                    if (output not in questions):
                        turn += 1
                        questions.append(output)
                        sentence_roots.append(sen)

            elif (turn % 3 == 1):
                if (meets_who_crit(sen, iter)):
                    output = generate_who_question(sen, man, woman, entity)
                    if (output != None) and (output not in questions):
                        turn += 1
                        questions.append(output)
                        sentence_roots.append(sen)

            elif (turn % 3 == 2):
                if (random.randint(1,4) == 1):
                    if (when_questions != None):
                        if (len(when_questions) != 0):
                            turn += 1
                            questions.append(when_questions.pop(0))
                elif (meets_when_crit(sen, iter)):
                    output = generate_when_question(sen)
                    if (output != None) and (output not in questions):
                        turn += 1
                        questions.append(output)
                        sentence_roots.append(sen)

        index += 1

    print("\n")
    for question in questions:
        print(str(question))
