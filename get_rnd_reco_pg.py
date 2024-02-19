import datetime
import random
from GuidelineService import GuidelineService
from html2text import HTML2Text

topic_dict = {
    "Diagnose": [ "Untersuchung",
        "Diagnostizieren",
        "Feststellen",
        "Diagnostische Verfahren",
        "Labor",
        "Pathologie",
        "Gewebeprobe",
        "Bildgebend",
        "Biopsie",
        "Histologie",
        "Zytologie",
        "Screening",
        "Früherkennung",
    ],
    "Behandlung": [
        "Behandlung",
        "Therapie",
        "Verfahren",
        "Intervention",
        "Medikation",
        "Medikament",
        "kurativ"
   ],
}

recos = {}
choices = []
service = GuidelineService()
loaded_guideline_dict = {}

def get_background_text(index, subsections):
    result = ""
    html2text = HTML2Text()
    last_index = -1
    #forward
    if (index < len(subsections)):
        for i in range(index + 1, len(subsections)):
            if subsections[i]['type'] == "TextCT" and (last_index < 0 or index == last_index + 1):
                result += " " + html2text.handle(subsections[i]['text']).replace("\r\n", " ").replace("\r"," ").replace("\n"," ").strip()
                last_index = i
    #backward
    if result is None and index > 0:
        for i in range(index - 1, 0, -1):
            if subsections[i]['type'] == "TextCT" and (last_index < 0 or index == last_index - 1):
                result = html2text.handle(subsections[i]['text']).replace("\r\n", " ").replace("\r"," ").replace("\n"," ").strip() + " " + result
                last_index = i

    return result.strip()

def get_gor(reco):
    if "statement" in reco['reco_type']:
        return "N/A"

    if reco['reco_type'] == "evidencebased-recommendation":
        if "title" in reco["recommendation_grade"] and reco["recommendation_grade"]["title"] is not None:
            return reco["recommendation_grade"]["title"]
        else:
            return "N/P"
    else:
        result = []
        if "können" in reco['text'] or "kann" in reco['text']:
            result.append("0")

        if "sollte" in reco['text']:
            result.append("B")
        elif "soll" in reco['text']:
            result.append("A")

        return ",".join(result)

def get_loe(reco):
    if 'consensbased' in reco['reco_type']:
        return "N/A"

    if "level_of_evidences" in reco and reco["level_of_evidences"] is not None:
        result = []
        for loe in reco["level_of_evidences"]:
            if 'internal_name' in loe['level_of_evidence'] and loe['level_of_evidence']['internal_name'] is not None:
                result.append(loe['level_of_evidence']['internal_name'])

        return ",".join(result)

def scan_recos(subsections):
    result = []
    for index in range(len(subsections)):
        subsection = subsections[index]
        if subsection['type'] == "RecommendationCT":
            subsection['text'] = HTML2Text().handle(subsection['text'])
            subsection['background'] = get_background_text(index, subsections)
            subsection['reco_type'] = subsection["type_of_recommendation"]["id"]
            subsection['gor'] = get_gor(subsection)
            subsection['loe'] = get_loe(subsection)
            result.append(subsection)
        if 'subsections' in subsection and subsection['subsections'] is not None:
            result.extend(scan_recos(subsection['subsections']))

    return result

def get_recos_with_background_texts(downloaded_guideline):
    result = scan_recos(downloaded_guideline['subsections'])
    return result

def chose_recos(N_RECO, reco_type):
    global loaded_guideline_dict
    result = []
    topic_index = -1
    while len(result) < N_RECO:
        topic_index += 1
        topic_index = topic_index % len(topic_dict)
        key_at_index = list(topic_dict)[topic_index]
        topic = topic_dict[key_at_index]
        guideline = random.choice(guideline_list)
        if guideline['short_title'] not in loaded_guideline_dict.keys():
            downloaded_guideline = service.download_guideline(guideline['id'], guideline_state="published", load_references=False)
            loaded_guideline_dict[guideline['short_title']] = get_recos_with_background_texts(downloaded_guideline)
            pass

        found = False
        test_counter = 0

        while not found and test_counter < len(loaded_guideline_dict[guideline['short_title']]):
            test_reco = random.choice(loaded_guideline_dict[guideline['short_title']])

            if test_reco['background'] is not None and len(test_reco['background']) > 0 and test_reco['reco_type'] == reco_type and test_reco not in result:
                if any(x in test_reco['text'] for x in topic):
                    found = True
            test_counter += 1

        if found:
            test_reco['guideline'] = guideline['short_title']
            test_reco['topic'] = key_at_index
            result.append(test_reco)

            out_csv = "%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % (
                test_reco['guideline'],
                test_reco['topic'],
                test_reco['number'].replace(".", "_"),
                test_reco['reco_type'],
                test_reco['gor'],
                test_reco['loe'],
                test_reco['text'].replace("\r\n", " ").replace("\r", " ").replace("\n", " ").strip(),
                test_reco['background'].replace("\r\n", " ").replace("\r", " ").replace("\n", " ").strip(),
                test_reco['uid'])

            today = datetime.datetime.now()
            with open("%s-%s-%s_random recos.csv" % (today.year, today.month, today.day), "a", encoding="utf-8") as f:
                f.write(out_csv)

            print("Topic %s: Added recommendation %s (%s/%s)" % (key_at_index, test_reco['number'], len(result), N_RECO ))

    return result

today = datetime.datetime.now()
out_csv = "Guideline|Topic|Nr|Type|GoR|LoE|Text|Background|UID\n"
with open("%s-%s-%s_random recos.csv" % (today.year, today.month, today.day), "w", encoding="utf-8") as f:
    f.write(out_csv)

guideline_list = [x for x in service.download_guideline_list() if x["guideline_language"]["id"] == "de"]

chose_recos(40, "evidencebased-recommendation")
chose_recos(40, "consensbased-recommendation")
