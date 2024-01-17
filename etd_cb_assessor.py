import datetime
import functools
import json
import os
from openai import Client
import time
from GuidelineService import GuidelineService
from html2text import HTML2Text

html2text = HTML2Text()

today = datetime.datetime.now()

def process_subsection(subsections, subsection):
    global out_file
    if subsection['type'] == "RecommendationCT":
        (reco_type, assessment) = get_assessment(guideline['short_title'], subsection, subsections)
        if reco_type is not None:
            f = open(out_file, "a", encoding="utf-8")
            f.write(assessment + "\n")
            f.close()

    if 'subsections' in subsection:
        process_subsections(subsection['subsections'])

def process_subsections(subsections):
    for subsection in subsections:
        process_subsection(subsections, subsection)

def get_background_text(reco, subsections):
    reco_index = subsections.index(reco)
    offset = 1
    index = reco_index

    text = None
    while index + offset < len(subsections) and text is None:
        if subsections[index + offset]['type'] == "TextCT":
            text = html2text.handle(subsections[index + offset]['text'])
        offset += 1

    if text is not None:
        if index + offset < len(subsections) and subsections[index + offset]['type'] == "TextCT":
            text += " " + html2text.handle(subsections[index + offset]['text'])
    else:
        index = reco_index
        while index - offset >= 0 and text is None:
            if subsections[index - offset]['type'] == "TextCT":
                text = html2text.handle(subsections[index - offset]['text'])
            offset += 1
        if text is not None:
            if index - offset >= 0 and subsections[index - offset]['type'] == "TextCT":
                text += " " + html2text.handle(subsections[index - offset]['text'])

    if text is None:
        index = reco_index
        while index + offset < len(subsections) and text is None:
            if subsections[index + offset]['type'] == "TableCT":
                text = html2text.handle(subsections[index + offset]['text'])
            offset += 1

        if text is not None:
            if index + offset < len(subsections) and subsections[index + offset]['type'] == "TextCT":
                text += " " + html2text.handle(subsections[index + offset]['text'])
        else:
            index = reco_index
            while index - offset >= 0 and text is None:
                if subsections[index - offset]['type'] == "TableCT":
                    text = html2text.handle(subsections[index - offset]['text'])
                offset += 1
            if text is not None:
                if index - offset >= 0 and subsections[index - offset]['type'] == "TextCT":
                    text += " " + html2text.handle(subsections[index - offset]['text'])
    return text.strip()

def parse_gor(reco_text):
    if "sollte" in reco_text:
        reco_gor = "B"
    elif "soll" in reco_text:
        reco_gor = "A"
    elif "kann" in reco_text or "können" in reco_text:
        reco_gor = "0"
    else:
        reco_gor = "N/A"

    return reco_gor

def extract_json(text):
    # Find the start of the JSON block
    start_index = text.find("{")
    if start_index == -1:
        return "JSON block not found."

    # Find the end of the JSON block
    end_index = text.rfind("}")
    if end_index == -1:
        return "JSON block not found."

    # Extract and return the JSON block
    return text[start_index:end_index + 1]

def get_assessment(guideline_title, reco, subsections):
    print("Processing recommendation %s" % reco['number'])
    reco_type = reco['type_of_recommendation']['id']
    reco_number = reco['number'].replace(".", "_")
    if reco_number in cb_reco_list or 'statement' in reco_type or 'evidence' in reco_type:
        return (None, None)
    reco_text = html2text.handle(reco['text']).replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    reco_type = "consensus-based"
    reco_loe = "N/A"
    reco_literature = "none"
    if 'statement' in reco['type_of_recommendation']['id']:
        reco_gor = "N/A"
    else:
        reco_gor = parse_gor(reco_text)

    param_list = ["clarityAndActionability",
                  "necessityInHealthcare",
                  "netPositiveConsequence",
                  "opportunityCost",
                  "rationaleForIndirectEvidence",
                  "justificationForStrengthOfRecommendation"
                  ]

    reco_background_text = get_background_text(reco, subsections)
    if reco_background_text is None:
        reco_background_text = "No background text"
    else:
        reco_background_text = reco_background_text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")

    messag_content = "GoR: %s, Rtext: %s, Btext: %s" % (reco_gor, reco_text, reco_background_text)
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": messag_content,
            }
        ]
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id="asst_u90HBHegSrIAmyfBMo2j6sbN",
    )

    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
            timeout=10
        )

        time.sleep(2)

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    text_val = extract_json(messages.data[0].content[0].text.value)
    etd_json = json.loads(text_val)

    result = "%s|%s|%s|%s|%s|%s|%s|" % (guideline_title, reco_number, reco_type, reco_gor, reco_loe, reco_text, reco_background_text)
    for param in param_list:
        result += "%s|%s|" % (etd_json['etdAssessment'][param]['explanation'], etd_json['etdAssessment'][param]['grade'])

    return (reco_type, result)

client = Client(api_key="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")
service = GuidelineService()

guideline = service.download_guideline("diagnostik-therapie-praevention-und-nachsorge-des-oro-und-hypopharynxkarzinoms", "private")

out_csv_cb = "Guideline|Nr|Type|GoR|LoE|RText|BText|clarityAndActionability||necessityInHealthcare||netPositiveConsequence||opportunityCost||rationaleForIndirectEvidence||justificationForStrengthOfRecommendation||\n"

cb_reco_list = []

out_file = "%s-%s-%s_etd_assessment_cb.csv" % (today.year,today.month, today.day)

if os.path.exists(out_file) == False:
    f = open(out_file, "a", encoding="utf-8")
    f.write(out_csv_cb)
    f.close()
else:
    f = open(out_file, "r", encoding="utf-8")
    reco_list = f.readlines()
    f.close()
    for reco in reco_list:
        item_arr = reco.split("|")
        cb_reco_list.append(item_arr[1])

process_subsections(guideline['subsections'])