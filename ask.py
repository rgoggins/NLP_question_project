'''
@file ask.py
@brief A python script for generating questions about a given document

11-411: Natural Language Processing

@author Ryan Goggins <goggins@cmu.edu>
@author Casey Al-Haddad <chaddad@andrew.cmu.edu>
@author Justin Lee <justinl2@andrew.cmu.edu>
@author Oliver Pennington <oop@cmu.edu>

'''

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

filename = "" #documents

tk = Tokenizer(filename)

sentiment_q = False


def generate_binary_question(root_sentence):
    # Of the format 'is it correct'

    if (sentiment_q == False):
        pass

    phrase = "Is it correct that "




questions = []

def generate_questions(ques_int):
    for entry in range(ques_int):
        root_sen =
        questions.append(generate_binary_question)
