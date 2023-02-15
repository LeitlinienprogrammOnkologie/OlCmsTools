import openai
import json
from PllUnderstandability.PllWordFileParser import PllWordFileParser
from PllUnderstandability.S3WordFileParser import S3WordFileParser
from PllUnderstandability.BrWordFileParser import BrWordFileParser
from readcalc import readcalc
from PllUnderstandability.TextParser import IndexCalculator
from PllUnderstandability.IgnorableChapterConstructor import IgnorableChapterConstructor
from PllUnderstandability.TextParser import ReadabilityMetrics
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

openai.api_key = "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"
model_engine = "text-davinci-003"

'''
prompt = "Until further notice, switch to German language"
completion = openai.Completion.create(
    engine=model_engine,
    prompt=prompt,
    max_tokens=4096-len(prompt),
    n=1,
    stop=None,
    temperature=0.5,
)

response = completion.choices[0].text
'''
pass

with open("source_text_paths.txt", "r", encoding="utf-8") as f:
    source_file_list = json.load(f)

def analyze_paragraphs(paragraph_dict):
    index_calculator = IndexCalculator()
    out_dict = {}
    for key, text_list in paragraph_dict.items():
        for text in text_list:
            metrics = index_calculator.Handle(text)
            if metrics is not None:
                if key not in out_dict:
                    out_dict[key] = {}
                out_dict[key][text] = metrics

    return out_dict

out_csv = "Leitlinie|Typ|Kapitel 1|Kapitel 2|Chars|Words|Types|Sentences|Syllables|Polysyllable Words|Difficult Words|Words > 4|Words > 6|Words > 10|Words > 13\n"

def add_to_csv(out_dict, guideline, type):
    result = ""
    for k, v in out_dict.items():
        chapter_1 = k
        for k1, v1 in v.items():
            chapter_2 = k1
            chapter_2 = ""
            if "Die Indikation für eine psychoonkologische Versorgung erfolgt" in chapter_2:
                pass
            if v1.number_words > 0:
                result += "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % (
                    guideline,
                    type,
                    chapter_1,
                    chapter_2,
                    v1.number_chars,
                    v1.number_words,
                    v1.number_types,
                    v1.number_sentences,
                    v1.number_syllables,
                    v1.number_polysyllable_words,
                    v1.difficult_words,
                    v1.number_words_longer_4,
                    v1.number_words_longer_6,
                    v1.number_words_longer_10,
                    v1.number_words_longer_13
                )
    return result

def translate_text_to_easy_langage(text):
    prompt = "Folgenden Text in leichte Sprache umwandeln: %s" % text
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=4096-len(prompt),
        n=1,
        stop=None,
        temperature=0.5,
    )

    response = completion.choices[0].text
    return response

def translate_dict(item_dict):
    for k, v in out_dict.items():
        for k1, v1 in v.items():
            pass

for guideline in source_file_list['files']:

    parser = PllWordFileParser()
    paragraph_dict = parser.Parse(guideline['pll'])
    out_dict = analyze_paragraphs(paragraph_dict)
    out_csv += add_to_csv(out_dict, guideline['title'], 'PLL')

    translate_dict(paragraph_dict)
    out_csv += add_to_csv(out_dict, guideline['title'], 'EASY')

    parser = S3WordFileParser()
    paragraph_dict = parser.Parse(guideline['s3'])
    out_dict = analyze_paragraphs(paragraph_dict)
    out_csv += add_to_csv(out_dict, guideline['title'], 'S3L')

    if len(guideline['br']) > 0:
        parser = BrWordFileParser()
        paragraph_dict = parser.Parse(guideline['br'])
        out_dict = analyze_paragraphs(paragraph_dict)
        out_csv += add_to_csv(out_dict, guideline['title'], 'BR')

    with open("count_results.csv", "w", encoding="utf-8") as f:
        f.write(out_csv)



