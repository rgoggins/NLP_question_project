"""
@file answer.py
@brief A python script for generating answers to a series of questions
11-411: Natural Language Processing
@author Oliver Pennington <oop@cmu.edu>
@author Ryan Goggins <goggins@cmu.edu>
@author Casey Al-Haddad <chaddad@andrew.cmu.edu>
@author Justin Lee <justinl2@andrew.cmu.edu>
"""

import nltk
nltk.download("punkt", quiet = True)
nltk.download("averaged_perceptron_tagger", quiet = True)
from spacy import load
from textblob import Word
from textblob import TextBlob
EN_CORE_WEB_VERSION = "md" #'sm', 'md', or 'lg' -- change this to whatever
nlp = load("en_core_web_" + EN_CORE_WEB_VERSION)

# Each question will fall under one of the categories below
PERSON_QUESTION = "PERSON"
YES_NO_QUESTION = "YN"
PLACE_QUESTION = "PLACE"
TIME_QUESTION = "TIME"
OBJECT_QUESTION = "OBJECT"
WHO_IS_QUESTION = "WHO IS"
OTHER = "OTHER"
QUANTITY_QUESTION = "QUANT"

#useful token tags for classifying questions
person_tags = ["PERSON"]
place_tags = ["GPE", "LOC"]
object_tags = ["ORG", "GPE", "LOC"]

class Answer:
    # Tokenizing, tagging, and sentence breakdown done with TextBlob and spaCy
    def __init__(self, textfile):
        corpus = textfile.replace("\n", ". ").replace(".", ".\n")
        self.corpus = corpus
        self.tb = TextBlob(corpus)
        self.NLP = nlp(corpus)

    # Checks if a question is of the form "Who is ____?"
    def is_who_is(self, w):
        if w[0].text.lower() == "who":
            if str(w[1].lemma_) == "be":
                el = w.ents
                if len(list(el)) == 1:
                    if str(el[0].label_) == "PERSON":
                        cands = " ".join([str(x) for x in list(w)[2:]]).replace("?", " ").strip()
                        found_s = str(el[0]).strip()
                        if  cands == found_s:
                            return (True, found_s)
        return (False, "")

    # return list of sentences sorted by relevance to question
    def get_relevant_sentences(self, question):
        a = set(TextBlob(question).words)
        snts = self.tb.sentences
        return sorted(snts, key = lambda sent: (len(a - set(sent.words)), len(list(TextBlob(question).words))))

    # returns exactly ONE sentence that is most relevant to question
    def get_relevant_sentence(self, question):
        most_relevant = None
        lowest_edit_dist = float('inf')
        a = set(TextBlob(question).words)
        for sent in self.tb.sentences:
            sentstr = str(sent)
            b = set(sent.words)
            missing = a - b
            levenshtein = len(missing)
            if (levenshtein < lowest_edit_dist):
                lowest_edit_dist = levenshtein
                most_relevant = sent
        return most_relevant

    # classifies question into one of the following categories: PERSON_QUESTION, YES_NO_QUESTION, PLACE_QUESTION ,
    # TIME_QUESTION, OBJECT_QUESTION, WHO_IS_QUESTION, QUANTITY_QUESTION, OTHER
    # Classification is done by identifying certain sentence structures and/or keywords
    def identify_question_type(self, qcorpus):
        person_words = ["who", "whom", "whose"]
        individual_words = ["person","pharoah", "congressman", "president", "leader", "senator", "actor", "businessman",
                            "author"]
        place_words = ["where"]
        location_words = ["place", "country", "region", "state", "city","continent", "stadium", "building","town",
                          "forest", "desert", "jungle", "lake", "ocean", "area", "location", 'planet','country','canal',
                          'hotel', 'seaport', 'residence', 'river', 'hamlet', 'bay', 'county', 'street', 'island',
                          'mountain', 'capital', 'sea', 'nation']
        time_words = ["when"]
        object_words = ["what", "which"]
        date_words = ["day", "date", "month", "year", "era", "time", "period", "season", "epoch", "eon","century",
                     "decade"]
        yes_no_words = set(["is", "does", "are", "was", "were", "did", "has", "could", "will", "have","can"])
        OBJ_CAND = "obj_cand"
        quantity_words = ["much", "many"]
        qType = OTHER
        if qcorpus[0].text.lower() in yes_no_words:
            qType = YES_NO_QUESTION
            return qType
        obj_ind = -1
        for i,w in enumerate(qcorpus):
            if (i == 4):
                break;
            word = w.text.lower()
            next_wordobj = w if i+1 >= len(qcorpus) else qcorpus[i + 1]
            next_word = next_wordobj.text.lower()
            if word in person_words:
                qType = PERSON_QUESTION
                break
            if word in place_words:
                qType = PLACE_QUESTION
                break
            if word in time_words:
                qType = TIME_QUESTION
                break
            if word == "how" and (next_word in quantity_words or next_wordobj.pos_ == "ADJ"):
                qType = QUANTITY_QUESTION
                break
            if word in object_words:
                qType = OBJ_CAND
                obj_ind = i
                break
        if qType == PERSON_QUESTION:
            (is_who_is_flag, subj) = self.is_who_is(nlp(str(qcorpus)))
            if is_who_is_flag:
                qType = WHO_IS_QUESTION
        if qType == OBJ_CAND:
            for i in range(min(len(qcorpus), obj_ind + 6)):
                w_obj = qcorpus[i]
                word = w_obj.text.lower()
                lw = str(w_obj.lemma_).lower()
                if  lw in date_words:
                    qType = TIME_QUESTION
                    break
                if lw in location_words:
                    qType = PLACE_QUESTION
                    break;
                if lw in individual_words:
                    qType = PERSON_QUESTION
                    break
        if qType == OBJ_CAND:
            qType = OBJECT_QUESTION
        return qType

    # finds index of closest instance of sub relative to index ind in string sent
    def find_closest_ind(self, sent, sub, ind):
        ans = []
        ci = 0
        while ci < len(sent):
            ofs = sent[ci:].find(sub)
            if ofs == -1:
                break
            ci += ofs
            ans.append(ci)
            ci += 1
        return min(ans, key = lambda x: abs(x - ind), default = abs(-1 - ind))

    # returns a score for an answer given the sentence its embedded within and the question
    def centrality_measure(self, ind, ent, sentence, spe):
        imp_phrase = list(list(sentence.noun_chunks)[0])
        if len(list(imp_phrase)) > 2:
            imp_phrase = list(imp_phrase)[2:]
        tot_score = 0
        for imp_word in imp_phrase:
            word_ind = str(spe.text.lower()).find(ent.text.lower())
            imp_word_ind = self.find_closest_ind(str(spe.text.lower()), str(imp_word.text).lower(), word_ind)
            score = 0
            if imp_word_ind == -1:
                score = abs(imp_word_ind - word_ind)/100
            else:
                score = abs(imp_word_ind - word_ind)
            tot_score += score
        return tot_score

    # selects the best generated answer for the question, based on certain scores calculated for each answer
    def select_best(self, spe, tags, question, rs):
        match_entities = []
        for i, entity in enumerate(spe):
            if entity.label_ in tags and str(entity.text).lower() not in str(question.text).lower():
                match_entities.append((self.centrality_measure(i,entity,question, rs), entity))
        return min(match_entities, key=lambda obj: obj[0], default=(None, None))[1]

    # answers questions about a person entity
    def answer_person_question(self, question, relevant_sentences):
        for sp in relevant_sentences:
            rs = nlp(str(sp))
            selected_passage_ents = rs.ents
            best = self.select_best(selected_passage_ents, person_tags, question, rs)
            if best != None:
                return best.text
        return None

    # answers questions about a location entity
    def answer_place_question(self, question, relevant_sentences):
        for sp in relevant_sentences:
            rs = nlp(str(sp))
            selected_passage_ents = rs.ents
            best = self.select_best(selected_passage_ents, place_tags, question, rs)
            if best != None:
                return best.text
        return None

    # answers a question looking for a date, time, or time period
    def answer_time_question(self,question, relevant_sentences):
        for sp in relevant_sentences:
            rs = nlp(str(sp))
            selected_passage_ents = rs.ents
            best = self.select_best(selected_passage_ents, ["DATE"], question, rs)
            if best != None:
                return best.text
            best = self.select_best(selected_passage_ents, ["CARDINAL"], question, rs)
            if best != None:
                return best.text
        return None

    # answers questions categorized as "OTHER"
    def answer_arb_question(self, question, relevant_sentences):
        return relevant_sentences[0]

    # answers questions where the answer is some sort of numerical quantity
    def answer_quantity_question(self, question, relevant_sentences):
        tags = ["QUANTITY", "CARDINAL", "MONEY", "PERCENT", "ORDINAL"]
        relevant_sents = [nlp(str(sp)) for sp in relevant_sentences]
        for tag in tags[0:3]:
            for rs in relevant_sents[0:10]:
                spe = rs.ents
                best = self.select_best(spe, [tag], question, rs)
                if best != None:
                    return best.text
        for tag in tags:
            for rs in relevant_sents[0:4]:
                spe = rs.ents
                spe_match = self.select_best(spe, [tag], question)
                if best != None:
                    return best.text
        return None

    # answers questions where the answer is either yes or no
    def answer_yes_no_question(self, qcorpus, tk, relevant_sentences):
        relevant_sentence = nlp(str(relevant_sentences[0]))
        q_tags = tk.tags
        keyword = ""
        key_tag = ""
        for (token, tag) in q_tags:
            if tag[0] == 'N' or tag[0] == "V":
                keyword = token
                key_tag = tag
        keyword_found = False
        neg = False
        for token in relevant_sentence:
            if str(token) == keyword or (key_tag[0] == "V" and Word(str(token)).lemmatize("v") == Word(keyword).lemmatize("v")):
                keyword_found = True
            if token.dep_ == 'neg':
                neg = not neg
        if keyword_found:
            if neg: return "No"
            else: return "Yes"
        return "No"

    # answers questions of the form "Who is ___?"
    def answer_who_is_question(self, qcorpus, relevant_sentences):
        per = list(qcorpus)[2:-1]
        for i in range(len(per)):
            np = [str(x) for x in per[i:]] + ["is"]
            for s in relevant_sentences:
                snlp = nlp(str(s))
                if len(list(snlp)) >= len(np):
                    ws = [str(x) for x in snlp[0:len(np)]]
                    for (sw, tw) in zip(np, ws):
                        if sw.lower() != tw.lower():
                            continue
                    return str(s)
        return None

    #NOTE: final version will only have self and question parameter.
    def answer_question(self, question):
        #tokenize question
        tk = TextBlob(question)
        qcorpus = nlp(question)
        #get sentence most relevant to the question
        relevant_sentence = str(self.get_relevant_sentence(question))

        #Identify question type:
        qType = self.identify_question_type(qcorpus)
        try:
            spes = self.get_relevant_sentences(question)
            answer = None
            if qType is PERSON_QUESTION:
                answer = self.answer_person_question(qcorpus, spes)
            elif qType is PLACE_QUESTION:
                answer = self.answer_place_question(qcorpus, spes)
            elif qType is TIME_QUESTION:
                answer = self.answer_time_question(qcorpus, spes)
            elif qType is YES_NO_QUESTION:
                answer = self.answer_yes_no_question(qcorpus, tk, spes)
            elif qType is QUANTITY_QUESTION:
                answer = self.answer_quantity_question(qcorpus, spes)
            elif qType is WHO_IS_QUESTION:
                answer = self.answer_who_is_question(qcorpus, spes)
            else:
                answer = self.answer_arb_question(qcorpus, spes)

            if answer == None:
                answer = self.answer_arb_question(qcorpus, spes)
                if answer == None:
                    return "Unsure."
                return answer
            else:
                return answer
        except:
            try:
                spes = self.get_relevant_sentences(question)
                answer = self.answer_arb_question(qcorpus, spes)
                if answer == None:
                    return "Unsure."
                else:
                    return answer
            except:
                return "Unsure."
