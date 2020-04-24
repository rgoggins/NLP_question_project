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
            if (i > 0) and (sentencestr[i-1].lower() == "the"):
                newsent = newsent[:-1]
                newsent.append("which year of the")
                continue
            if (i > 0) and (sentencestr[i-1].lower() in ["in", "on"]):
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



def generate_who_question(root_sentence):
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
                return "who"
            else:
                # Replace with he or his (appropriate pronoun)
                return "who"
        else:
            return "he"
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

questions = []

sentence_roots = []



if __name__ == "__main__":
    filename = str(sys.argv[1])
    num_questions = int(sys.argv[2])

    tk = Tokenizer(filename)

    index = 0

    while (len(questions) < num_questions):
        sen = tk.blob.sentences[index % len(tk.blob.sentences)]

        if (meets_binary_crit(sen)):
            questions.append(generate_binary_question(sen))
            sentence_roots.append(sen)
        elif (meets_who_crit(sen)):
            output = generate_who_question(sen)
            if (output != None):
                questions.append(output)
                sentence_roots.append(sen)
        elif (meets_when_crit()):
            output = generate_when_question(sen)
            if (output != None):
                questions.append(output)
                sentence_roots.append(sen)
        elif (meets_where_crit()):
            

        # print("Len of questions: " + str(len(questions)))
        # print("Sentence " + str(index) + " w polarity " + str(sen.sentiment.polarity) + " is " + str(sen[:min(40,len(sen))]))
        if (abs(sen.sentiment.polarity) > (0.9**index)) and ('\n' not in str(sen)) and ("PRP" not in sen.tags[0][1]):
            # if (index < len(tk.blob.sentences)):
            questions.append(generate_binary_question(sen))
            sentence_roots.append(sen)
        elif ('\n' not in str(sen)) and (abs(sen.sentiment.polarity) >0.1) and (len(sen.words) > 10):
            # print("Len of sen: " + str(len(sen.words)))
            output = generate_who_question(sen)
            if (output != None):
                questions.append(output)
                sentence_roots.append(sen)
        else:
            output = generate_when_question(sen)
            if (output != None):
                questions.append(output)
                sentence_roots.append(sen)

        index += 1

    print("\n")
    for question in questions:
        print(str(question))
