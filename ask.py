'''
@file ask.py
@brief A python script for generating questions about a given document

11-411: Natural Language Processing

@author Ryan Goggins <goggins@cmu.edu>
@author Casey Al-Haddad <chaddad@andrew.cmu.edu>
@author Justin Lee <justinl2@andrew.cmu.edu>
@author Oliver Pennington <oop@cmu.edu>

'''

# Passed in documents and a number 'n' of questions we are required to generate
# Load in the tokenized data
# Create NER table
# Find most frequent entities referenced by document
# Split up questions equally into Who? What? Is/was? (only binary questions for now)
# A question should have its answer in a single sentence

import tokenizer
