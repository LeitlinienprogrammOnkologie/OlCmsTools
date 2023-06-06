from GuidelineService import GuidelineService
from bs4 import BeautifulSoup

service = GuidelineService()

guideline_list = service.download_guideline_list()

current_chapter_level = -1
current_chapter_list = ["", "", ""]

out_csv = "Leitlinie|Kapitel 1|Kapitel 2|Kapitel 3|Nummer|Text|Typ|LoE|GoR\n"

def get_reco_string(reco):
    return "%s"

def scan_subsections(subsection_list):
    global out_csv, current_chapter_list, current_chapter_level
    current_chapter_level += 1

    for subsection in subsection_list:
        if subsection['type'] == "ChapterCT":
            if current_chapter_level < len(current_chapter_list):
                soup = BeautifulSoup(subsection['title'])
                current_chapter_list[current_chapter_level] = soup.get_text()

        if subsection['type'] == "RecommendationCT":
            soup = BeautifulSoup(subsection['text'])
            reco_type = subsection['type_of_recommendation']['name'] if ('type_of_recommendation' in subsection and 'name' in subsection['type_of_recommendation']) else ""
            if reco_type == "Evidenzbasierte Empfehlung":
                pass

            #reco = [guideline['short_title'], current_chapter_list[0], current_chapter_list[1], current_chapter_list[2], subsection['number'].replace(".","_"), soup.get_text(), reco_type]
            pass

        if "subsections" in subsection:
            try:
                scan_subsections(subsection['subsections'])
            except:
                pass

    current_chapter_level -= 1

for guideline in guideline_list:
    if guideline['state'] == "published" and guideline['guideline_language']['id'] == "de":
        guideline = service.download_guideline(guideline['id'], load_references=False)
        scan_subsections(guideline['subsections'])
