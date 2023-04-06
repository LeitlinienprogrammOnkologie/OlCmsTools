import numpy as np
import pandas as pd
from PllUnderstandability.TextParser import IndexCalculator
from HanTa.HanoverTagger import HanoverTagger
import nltk
nltk.download('tagsets')
from nltk.collocations import *

import spacy
import de_dep_news_trf

nlp = de_dep_news_trf.load()

tagger = HanoverTagger('morphmodel_ger.pgz')
index_calculator = IndexCalculator()

input_file = "//dkg-dc-01/Daten/Daten/Arbeitsverzeichnisse/OL/Vorträge/G-I-N 2023/Easy Language Guidelines with KI/2023-02-21_SUMM_PLL_DV3-Children_7 Words_no explanations.xlsx"

df = pd.read_excel(input_file)

for index, row in df.iterrows():
    pll_text = row['PLL-Text']
    if not isinstance(pll_text, str):
        metrics = index_calculator.Handle(pll_text)
        if metrics is not None:
            flesh_de = 180 - metrics.ASL - (58.5 * metrics.ASW)
            row['PLL-ASL'] = metrics.ASL
            row['PLL-ASW'] = metrics.ASW
            row['PLL-LIX'] = metrics.lix_index
            row['PLL-FLESH_DE'] = flesh_de

    pll_text = row['DV3-Text']
    if not isinstance(pll_text, str):
        continue
    metrics = index_calculator.Handle(pll_text)
    sentences = nltk.sent_tokenize(pll_text)
    for sent in sentences:
        doc = nlp(sent)
        word_doc = [(w.text, w.pos_) for w in doc]
        words = nltk.word_tokenize(sent)
        lemmata = tagger.tag_sent(words)

        pass
    if metrics is not None:
        flesh_de = 180 - metrics.ASL - (58.5 * metrics.ASW)
        row['DV3-ASL'] = metrics.ASL
        row['DV3-ASW'] = metrics.ASW
        row['DV3-LIX'] = metrics.lix_index
        row['DV3-FLESH_DE'] = flesh_de
        pass
    df.iloc[index] = row
df.to_excel(input_file)