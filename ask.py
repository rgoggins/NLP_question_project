#!/usr/bin/python3
'''
@file ask.py
@brief A python script for generating questions about a given document

11-411: Natural Language Processing

@author Ryan Goggins <goggins@cmu.edu>
@author Casey Al-Haddad <chaddad@andrew.cmu.edu>
@author Justin Lee <justinl2@andrew.cmu.edu>
@author Oliver Pennington <oop@cmu.edu>

'''
import re
import math
import sys
import random
from tokenizer import *
import nltk

# Passed in documents and a number 'n' of questions we are required to generate
# Load in the tokenized data
# Create NER table
# Find most frequent entities referenced by document
# Split up questions equally into Who? What? Is/was? (only binary questions for now)
# A question should have its answer in a single sentence


tokenized_data = None # call whatever tokenizer.py function gets the data
num_questions = 10 # this is also passed in

sent = "Although no announcement was made by his team, Ryan Dempsey appeared in the Seattle squad to face Sporting in the season opener on March 10, 2014."

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
    newsent = []
    print("Sentence: " + str(sentencestr))

    for i, word in enumerate(sentencestr):
        if (len(word) == 4 and word.isdigit() and (word[:2] in ["18", "19", "20"])):
            year = int(word)
            ind = i
            # replace it
            print("Previous: " + str(sentencestr[i-1]))
            if (i > 0) and (i < len(root_sentence.words) - 1):
                if (sen.tags[i-1][1] == "NN") and (sen.tags[i+1][1] == "NN"):
                    return None

            if (i > 0) and (sentencestr[i-1].lower() == "the"):
                newsent = newsent[:-1]
                newsent.append("which year of the")
                continue
            if (i > 0) and (sentencestr[i-1].lower() in ["in", "on", "between"]):
                newsent.append("what year")
                continue
            else:
                newsent.append("in which year")
                continue
        else:
            newsent.append(word)

    if (year == None):
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


def generate_binary_question(root_sentence):
    phrase = "Is it correct that "
    sent_frag = str(root_sentence)
    def fn_replacement(m):
        value = m.group(0)
        # print("Value is " + str(value))
        if (random.randint(1,2) == 1):
            number = int(value)
            if (abs(number - 1990) < 30):
                return " " + str(random.randint(1,30) + 1990) + ""
            return " " + str(number*2) + " "
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
    return (len(sentence.words) > 15 - iter) and ('\n' not in str(sentence)) and (sen.tags[0][1] not in invalid_starting_labels) and (abs(sen.sentiment.polarity) >0.4 - float(iter)/10.0)

def meets_who_crit(sentence, iter):
    return ('\n' not in str(sentence)) and (sen.tags[0][1] not in invalid_starting_labels) and (abs(sen.sentiment.polarity) >0.3 - float(iter)/10.0) and (len(sentence.words) > 10)

def meets_when_crit(sentence, iter):
    return (len(sentence.words) > 15 - iter) and ('\n' not in str(sentence)) and (sen.tags[0][1] not in invalid_starting_labels)


questions = []

sentence_roots = []



if __name__ == "__main__":
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

    index = 0

    while (len(questions) < num_questions):
        iter = (index // len(tk.blob.sentences))
        sen = tk.blob.sentences[index % len(tk.blob.sentences)]
        print("Sentence: " + str(sen))
        print("Sentence tags: " + str(sen.tags))
        print("\n")
        if (meets_binary_crit(sen, iter)):
            output = generate_binary_question(sen)
            if (output not in questions):
                questions.append(output)
                sentence_roots.append(sen)
        elif (meets_who_crit(sen, iter)):
            output = generate_who_question(sen, man, woman, entity)
            if (output != None) and (output not in questions):
                questions.append(output)
                sentence_roots.append(sen)
        elif (meets_when_crit(sen, iter)):
            output = generate_when_question(sen)
            if (output != None) and (output not in questions):
                questions.append(output)
                sentence_roots.append(sen)

        index += 1

    print("\n")
    for question in questions:
        print(str(question))
