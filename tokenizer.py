from textblob import TextBlob

class Tokenizer:
    def __init__(self, input_file):
        f = open(input_file, "r+", encoding="utf-8")
        text = f.read()
        self.blob = TextBlob(text)


###  Below are the basics for textBlobs
###  They tokenize the text, split it to sentences, and do POS tagging all in one.
###  Also does sentiment analysis on sentences if we ever need that
#    https://textblob.readthedocs.io/en/dev/quickstart.html#quickstart
