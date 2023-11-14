from GuidelineService import GuidelineService
from bs4 import BeautifulSoup

service = GuidelineService()

guideline_list = service.download_guideline_list()

current_chapter_level = -1
current_chapter_list = ["", "", ""]
current_topic = "Anderes"

out_csv = "Leitlinie|Kapitel 1|Kapitel 2|Kapitel 3|Thema|Nummer|Text|Typ|LoE|GoR\n"

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

def scan_subsections(subsection_list):
    global out_csv, current_chapter_list, current_chapter_level, current_topic
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
            if "Evidenzbasiert" in reco_type:
                if "Empfehlung" in reco_type:
                    if 'recommendation_grade' in subsection and subsection['recommendation_grade'] is not None and 'title' in subsection['recommendation_grade'] and subsection['recommendation_grade']['title'] is not None:
                        reco_gor = subsection['recommendation_grade']['title']
                if 'level_of_evidences' in subsection and subsection['level_of_evidences'] is not None:
                    loe_list = subsection['level_of_evidences']
                    reco_loe = ",".join([x['level_of_evidence']['title'] for x in loe_list if x['level_of_evidence'] is not None])
            else:
                if "sollte" in reco_text:
                    reco_gor = "B"
                elif "soll" in reco_text:
                    reco_gor = "A"
                elif "kann" in reco_text or "können" in reco_text:
                    reco_gor = "0"

            reco = [guideline['short_title'], current_chapter_list[0], current_chapter_list[1], current_chapter_list[2], current_topic, subsection['number'].replace(".","_"), reco_text, reco_type, reco_loe, reco_gor]
            out_csv += "|".join(reco)+"\n"
        pass

        if "subsections" in subsection:
            try:
                scan_subsections(subsection['subsections'])
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")

    current_chapter_level -= 1

for guideline in guideline_list:
    if guideline['state'] == "published" and guideline['guideline_language']['id'] == "de":
        guideline = service.download_guideline(guideline['id'], load_references=False)
        #guideline = service.load_guideline(guideline['id'])
        scan_subsections(guideline['subsections'])
        f = open("reco_list.csv", "w")
        f.write(out_csv)
        f.close()
        print(guideline['short_title']+" fertig.")