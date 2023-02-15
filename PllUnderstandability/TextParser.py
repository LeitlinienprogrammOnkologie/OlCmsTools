import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from readcalc import readcalc

#nltk.download()

class ReadabilityMetrics:
    def __init__(self, metrics):
        flesh_limit_dict = { 0: "very hard", 30: "hard", 60: "sophisticated", 70: "normal", 80: "basic", 90: "easy", 100: "very easy"}
        lix_limit_dict = {40: "children and youths", 50: "fiction", 60: "non-fiction", 1000: "technical"}
        if metrics[0] == 0:
            return

        self.number_chars = metrics[0]
        self.number_words = metrics[1]
        self.number_types = metrics[2]
        self.number_sentences = metrics[3]
        self.number_syllables = metrics[4]
        self.number_polysyllable_words = metrics[5]
        self.difficult_words = metrics[6]
        self.number_words_longer_4 = metrics[7]
        self.number_words_longer_6 = metrics[8]
        self.number_words_longer_10 = metrics[9]
        self.number_words_longer_13 = metrics[10]
        self.flesch_reading_ease = metrics[11]
        self.flesch_kincaid_grade_level = metrics[12]
        self.coleman_liau_index = metrics[13]
        self.gunning_fog_index = metrics[14]
        self.smog_index = metrics[15]
        self.ari_index = metrics[16]
        self.lix_index = metrics[17]
        self.dale_chall_score = metrics[18]

        self.flesch_de = (180 - (self.number_words / self.number_sentences)) - (58.5 * (self.number_syllables / self.number_words))

'''
        for k, v in flesh_limit_dict.items():
            if self.flesch_de <= k:
                self.flesch_grade = v
                break

        for k, v in lix_limit_dict.items():
            if self.lix_index <= k:
                self.lix_grade = v
                break
'''

class IndexCalculator:
    def __init__(self):
        nltk.data.load('tokenizers/punkt/german.pickle')
        nltk.data.load('taggers/averaged_perceptron_tagger/averaged_perceptron_tagger.pickle')
    def Handle(self, text):
        sents = nltk.sent_tokenize(text)
        any_verb = False
        for sent in sents:
            tokens = nltk.word_tokenize(sent)
            any_verb = any(filter(lambda x: "VB" in x[1], nltk.pos_tag(tokens)))
            if any_verb:
                break

        if any_verb:
            calc = readcalc.ReadCalc(text=text, language="de", preprocesshtml=None)
            metrics = ReadabilityMetrics(calc.get_all_metrics())
            return metrics
        else:
            return None