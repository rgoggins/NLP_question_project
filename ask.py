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

# Passed in documents and a number 'n' of questions we are required to generate
# Load in the tokenized data
# Create NER table
# Find most frequent entities referenced by document
# Split up questions equally into Who? What? Is/was? (only binary questions for now)
# A question should have its answer in a single sentence


tokenized_data = None # call whatever tokenizer.py function gets the data
num_questions = 10 # this is also passed in



# sentiment_q = False


def generate_binary_question(root_sentence):
    # Of the format 'is it correct'
    phrase = "Is it correct that "

    sent_frag = str(root_sentence)


    # Change the original sentence

    def fn_replacement(m):
        value = m.group(0)
        # print("Value is " + str(value))
        if (random.randint(1,2) == 1):
            number = int(value)
            if (abs(number - 1990) < 30):
                return " " + str(random.randint(1,30) + 1990)
            return " " + str(number*2) + ""
        else:
            return str(value)

    match = '\s\d\d*'


    sent_frag = re.sub(match, fn_replacement, str(root_sentence))

    word1 = root_sentence.tags[0]

    if (word1[1] != "NNP"):
        # print("First word is not a proper noun " + str(word1[0]))
        sent_frag = sent_frag[0].lower() + "" + sent_frag[1:]

    # sent_frag = sent_frag[0] + "" + sent_frag[1:]

    return phrase + sent_frag

questions = []

sentence_roots = []

# Add in names

if __name__ == "__main__":
    filename = str(sys.argv[1])
    num_questions = int(sys.argv[2])

    tk = Tokenizer(filename)

    index = 0

    while (len(questions) < num_questions):
        sen = tk.blob.sentences[index % len(tk.blob.sentences)]
        # print("Len of questions: " + str(len(questions)))
        # print("Sentence " + str(index) + " w polarity " + str(sen.sentiment.polarity) + " is " + str(sen[:min(40,len(sen))]))
        if (abs(sen.sentiment.polarity) > (0.8**index)) and ('\n' not in str(sen)) and ("PRP" not in sen.tags[0][1]):
            # if (index < len(tk.blob.sentences)):
            questions.append(generate_binary_question(sen))
            sentence_roots.append(sen)


        index += 1

    for question in questions:
        print(str(question))
