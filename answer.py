'''
@file answer.py
@brief A python script for generating answers to a series of questions
11-411: Natural Language Processing
@author Oliver Pennington <oop@cmu.edu>
@author Ryan Goggins <goggins@cmu.edu>
@author Casey Al-Haddad <chaddad@andrew.cmu.edu>
@author Justin Lee <justinl2@andrew.cmu.edu>
'''
import sys
import os
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
nltk.download("punkt", quiet = True)
nltk.download("averaged_perceptron_tagger", quiet = True)
#from edit_dist import *
from spacy import load
# from tokenizer import *
from textblob import Word
from textblob import TextBlob
EN_CORE_WEB_VERSION = "lg" #'sm', 'md', or 'lg' -- change this to whatever
nlp = load("en_core_web_" + EN_CORE_WEB_VERSION)
# from tokenizer import *
# DBG = True
PERSON_QUESTION = "PERSON"
YES_NO_QUESTION = "YN"
PLACE_QUESTION = "PLACE"
TIME_QUESTION = "TIME"
OBJECT_QUESTION = "OBJECT"
WHO_IS_QUESTION = "WHO IS"
OTHER = "OTHER"
QUANTITY_QUESTION = "QUANT"
person_tags = ["PERSON"]
place_tags = ["GPE", "LOC"]
object_tags = ["ORG", "GPE", "LOC"]
class Answer:
    def __init__(self, textfile):
        #TODO process corpus based on tokenization
        # f = open(textfile, "r+")
        # corpus = f.read()
        corpus = textfile.replace("\n", ". ").replace(".", ".\n")
        self.corpus = corpus
        self.tb = TextBlob(corpus)
        self.NLP = nlp(corpus)
    def is_who_is(self, w):
        if w[0].text.lower() == "who":
            if str(w[1].lemma_) == "be":
                el = w.ents
                if len(list(el)) == 1:
                    if str(el[0].label_) == "PERSON":
                        cands = " ".join([str(x) for x in list(w)[2:]]).replace("?", " ").strip()
                        found_s = str(el[0]).strip()
#                         print(cands, found_s)
                        if  cands == found_s:
                            return (True, found_s)
        return (False, "")
    def get_relevant_sentences(self, question):
        a = set(TextBlob(question).words)
        snts = self.tb.sentences
        return sorted(snts, key = lambda sent: (len(a - set(sent.words)), len(list(TextBlob(question).words))))
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
    def identify_question_type(self, qcorpus):
        person_words = ["who", "whom", "whose"]
        individual_words = ["person","pharoah", "congressman", "president", "leader", "senator", "actor", "businessman", "author"] #TODO
        place_words = ["where"]
        location_words = ["place", "country", "region", "state", "city","continent", "stadium", "building","town",
                          "forest", "desert", "jungle", "lake", "ocean", "area", "location", 'planet','country','canal',
                          'hotel', 'seaport', 'residence', 'river', 'hamlet', 'bay', 'county', 'street', 'island', 'mountain',
                          'capital', 'sea', 'nation']
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
        #TODO lemmatize words, check for stuff
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
#             print(is_who_is_flag, subj, qcorpus)
            if is_who_is_flag:
                qType = WHO_IS_QUESTION
#             if self.is_who_is(qcorpus)[0]:
#                 qType = WHO_IS_QUESTION
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
    #                 break
    #         for i,w in enumerate(qcorpus):
    #             word = w.text.lower()
    #             next_wordobj = w if i+1 >= len(qcorpus) else qcorpus[i + 1]
    #             next_word = next_wordobj.text.lower()
    #             if word in person_words:
    #                 qType = PERSON_QUESTION
    #                 break
    #             if word in place_words:
    #                 qType = PLACE_QUESTION
    #                 break
    #             if word in time_words:
    #                 qType = TIME_QUESTION
    #                 break
    #             if word == "how" and (next_word in quantity_words or next_wordobj.pos_ == "ADJ"):
    #                 qType = QUANTITY_QUESTION
    #                 break
    #             if word in object_words:
    #                 if next_word in date_words:
    #                     qType = TIME_QUESTION
    #                 elif next_word in location_words:
    #                     qType = PLACE_QUESTION
    #                 else:
    #                     qType = OBJECT_QUESTION
    #                 break
    #             if i == 5:
    #                 break;
#         print("qType is:", qType)
        return qType
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
#             print(sub, ci)
        return min(ans, key = lambda x: abs(x - ind), default = abs(-1 - ind))
    def centrality_measure(self, ind, ent, sentence, spe):
#         print("CM")
        imp_phrase = list(list(sentence.noun_chunks)[0])
        if len(list(imp_phrase)) > 2:
            imp_phrase = list(imp_phrase)[2:]
        tot_score = 0
#         imp_phrase_str = " ".join([str(ipw) for ipw in imp_phrase]).lower()
#         if imp_phrase_str in str(spe.text.lower()):
#             word_ind = str(spe.text.lower()).find(ent.text.lower())
#             imp_word_ind = find_closest_ind(str(spe.text.lower()), (imp_phrase_str), word_ind)
#             return abs(imp_word_ind - word_ind)
#         print(imp_phrase)
        for imp_word in imp_phrase:
#             print(imp_word)
            word_ind = str(spe.text.lower()).find(ent.text.lower())
            imp_word_ind = self.find_closest_ind(str(spe.text.lower()), str(imp_word.text).lower(), word_ind)
            #str(spe.text.lower()).find(str(imp_word).lower())
            score = 0
            if imp_word_ind == -1:
                score = abs(imp_word_ind - word_ind)/100
            else:
                score = abs(imp_word_ind - word_ind)
            tot_score += score
#             print(score, ent.text, imp_word, word_ind, imp_word_ind, spe)
        return tot_score
#         return ind
    def select_best(self, spe, tags, question, rs):
        match_entities = []
        for i, entity in enumerate(spe):
            if entity.label_ in tags and str(entity.text).lower() not in str(question.text).lower():
                match_entities.append((self.centrality_measure(i,entity,question, rs), entity))
        return min(match_entities, key=lambda obj: obj[0], default=(None, None))[1]
    def answer_person_question(self, question, relevant_sentences):
        for sp in relevant_sentences:
            rs = nlp(str(sp))
            selected_passage_ents = rs.ents
            best = self.select_best(selected_passage_ents, person_tags, question, rs)
            if best != None:
                return best.text
#             for entity in selected_passage_ents:
#                 if entity.label_ in person_tags and str(entity.text.lower()) not in str(question).lower():
#                     print(str(entity.text.lower()), str(question).lower())
#                     return entity.text
        return None
    def answer_place_question(self, question, relevant_sentences):
        for sp in relevant_sentences:
            rs = nlp(str(sp))
            selected_passage_ents = rs.ents
            best = self.select_best(selected_passage_ents, place_tags, question, rs)
            if best != None:
                return best.text
#             for entity in selected_passage_ents:
#                 if entity.label_ in place_tags:
#                     return entity.text
        return None
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
#             e
#             for entity in selected_passage_ents:
#                 if entity.label_ in ["DATE"]:
#                     return entity.text
#             for entity in selected_passage_ents:
#                 if entity.label_ in ["CARDINAL"]:
#                     return entity.text
        return None
    def answer_arb_question(self, question, relevant_sentences):
        return relevant_sentences[0]
#         for sp in relevant_sentences:
#             selected_passage_ents = nlp(str(sp)).ents
#             for entity in selected_passage_ents:
#                 return entity.text
#         return None
    def answer_quantity_question(self, question, relevant_sentences):
        tags = ["QUANTITY", "CARDINAL", "MONEY", "PERCENT", "ORDINAL"]
        relevant_sents = [nlp(str(sp)) for sp in relevant_sentences]
        for tag in tags[0:3]:
            for rs in relevant_sents[0:10]:
                spe = rs.ents
#                 spe_match = [entity for entity in spe if entity.label_ == tag]
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
        #WHICH?????
        # selected_passage_ents = nlp(relevant_sentence).ents
        # for entity in selected_passage_ents:
        #     print(entity.text, entity.label_)
        #Split into types of questions:
        #PERSON: (WHO)
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
                answer = self.answer_who_is_question(qcorpus, spes) #TODO change this
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
