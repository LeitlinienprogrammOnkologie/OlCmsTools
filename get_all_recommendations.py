import datetime

from GuidelineService import GuidelineService
from bs4 import BeautifulSoup

service = GuidelineService()

guideline_list = service.download_guideline_list(state="published")
guideline_list.extend(service.download_guideline_list(state="private"))
guideline_list.extend(service.download_guideline_list(state="consulted"))

current_chapter_level = -1
current_chapter_list = ["", "", ""]
current_topic = "Anderes"

out_csv = "Leitlinie|AWMF-ID|Status|ersion|Jahr|Fullname|Kapitel 1|Kapitel 2|Kapitel 3|Thema|Nummer|Text|Typ|LoE|SIGN|Oxford 2009|Oxford 2011|GRADE|GoR\n"

topic_dict = \
    {
        "Diagnostik" : ["Untersuchung", "Diagno", "endoskop"],
        "Klassifikation": ["Klassifi", "Stadien", "Histo", "Staging"],
        "Strahlentherapie": [["Therapie"], ["Strahlen", "Radio"]],
        "Medikamentöse Therapie": [["Therapie"], ["medikament", "chemo", "immun", "systemisch", "checkpoint", "inhibitor"]],
        "Chirurgische Therapie": [["Therapie"], ["operation", "chirurg"]],
        "Erstlinientherapie": ["Therapie", ["Erstlinie", "1st", "First"]],
        "Zweitlinientherapie": ["Therapie", ["Zweitlinie", "2nd", "Second"]],
        "Drittlinientherapie": ["Therapie", ["Drittlinie", "3rd", "Third"]],
        "Palliative Therapie": [["Therapie"], ["Palliativ"]],
        "Rezidivtherapie": [["Therapie"], ["Rezidiv"]],
        "Supportive Therapie": "Supportiv",
        "Rehabilitation": "Reha",
        "Epidemiologie": "Epidem",
        "Versorgungsstrukturen": "Versorgung",
        "Nachsorge": ["Nachsorge", "Follow-up"],
        "Kommunikation": ["Kommunikation, Gespräch"],
        "Therapie": "Therapieb"
    }

def get_topic(title):
    if "Strahlentherapie" in title:
        pass
    for key, value in topic_dict.items():
        if isinstance(value, str):
            if value.lower() in title.lower():
                return key
        else:
            if any([x for x in value if isinstance(x, list)]):
                if isinstance(value[0], str) and isinstance(value[1], list):
                    if value[0].lower() in title.lower() and any([x for x in value[1] if x.lower() in title.lower()]):
                        return key
                elif isinstance(value[1], str) and isinstance(value[0], list):
                    if value[1].lower() in title.lower() and any([x for x in value[0] if x.lower() in title.lower()]):
                        return key
                else:
                    if any([x for x in value[0] if x.lower() in title.lower()]) and any([x for x in value[1] if x.lower() in title.lower()]):
                        return key
            else:
                if any([x for x in value if x.lower() in title.lower()]):
                    return key

    return "Anderes"

def get_loe_types(loe_list):
    result = [0, 0, 0, 0]
    for loe in loe_list:
        if 'internal_name' in loe['level_of_evidence'] and loe['level_of_evidence']['internal_name'] is not None:
            name = loe['level_of_evidence']['internal_name']
            if "SIGN" in name:
                result[0] += 1
            elif "Oxford 2006"  in name or "Oxford 2009" in name:
                result[1] += 1
            elif "Oxford 2011" in name:
                result[2] += 1
            elif "GRADE" in name:
                result[3] += 1

    return result

def scan_subsections(subsection_list, state):
    global guideline, out_csv, current_chapter_list, current_chapter_level, current_topic
    current_chapter_level += 1

    for subsection in subsection_list:
        if subsection['type'] == "ChapterCT":
            if current_chapter_level < len(current_chapter_list):
                soup = BeautifulSoup(subsection['title'])
                current_chapter_list[current_chapter_level] = soup.get_text()
                if current_chapter_level < 2:
                    suggested_topic = get_topic(soup.get_text())
                    if current_chapter_level == 1 and suggested_topic != "Anderes":
                        current_topic = get_topic(soup.get_text())
                    else:
                        current_topic = get_topic(current_chapter_list[0])
                    pass
        elif subsection['type'] == "RecommendationCT":
            soup = BeautifulSoup(subsection['text'], features="lxml")
            reco_text = soup.get_text().replace("\r\n", "").replace("\r", "").replace("\n", "").strip()
            reco_type = subsection['type_of_recommendation']['name'] if ('type_of_recommendation' in subsection and 'name' in subsection['type_of_recommendation']) else ""
            reco_gor = ""
            reco_loe = ""
            reco_loe_types = [0, 0, 0, 0]
            if "Evidenzbasiert" in reco_type:
                if "Empfehlung" in reco_type:
                    if 'recommendation_grade' in subsection and subsection['recommendation_grade'] is not None and 'title' in subsection['recommendation_grade'] and subsection['recommendation_grade']['title'] is not None:
                        reco_gor = subsection['recommendation_grade']['title']
                if 'level_of_evidences' in subsection and subsection['level_of_evidences'] is not None:
                    loe_list = subsection['level_of_evidences']
                    reco_loe_types = get_loe_types(loe_list)
                    #reco_loe_types = ",".join([x['level_of_evidence']['title'] for x in loe_list if x['level_of_evidence'] is not None and 'title' in x['level_of_evidence'] and x['level_of_evidence']['title'] is not None])
            else:
                if "sollte" in reco_text:
                    reco_gor = "B"
                elif "soll" in reco_text:
                    reco_gor = "A"
                elif "kann" in reco_text or "können" in reco_text:
                    reco_gor = "0"

            guideline_date = datetime.datetime.fromisoformat(guideline['date'].rstrip('Z'))
            fullname = "%s V%s (%s)" % (guideline['short_title'], guideline['version'], guideline_date.year)
            reco = [guideline['short_title'], guideline['awf_registernumber'], state, guideline['version'], str(guideline_date.year), fullname, current_chapter_list[0], current_chapter_list[1], current_chapter_list[2], current_topic, subsection['number'].replace(".","_"), reco_text, reco_type, reco_loe, str(reco_loe_types[0]), str(reco_loe_types[1]), str(reco_loe_types[2]), str(reco_loe_types[3]), reco_gor]
            out_csv += "|".join(reco)+"\n"
        pass

        if "subsections" in subsection:
            try:
                scan_subsections(subsection['subsections'], state)
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")

    current_chapter_level -= 1

today = datetime.datetime.today()

for guideline in guideline_list:
    #if guideline['state'] == "published" and guideline['guideline_language']['id'] == "de":
    if guideline['guideline_language']['id'] == "de":
        state = guideline['state']
        try:
            guideline = service.download_guideline(guideline['id'], load_references=False, guideline_state=state)
            scan_subsections(guideline['subsections'], state)
            print("%s, state %s fertig." % (guideline['short_title'], state))
        except:
            print("%s, state %s nichtr verfügbar." % (guideline['short_title'], state))

f = open("%s-%s-%s_reco_list.csv" % (today.year, today.month, today.day), "w", encoding="utf-8")
f.write(out_csv)
f.close()