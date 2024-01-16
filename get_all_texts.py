from GuidelineService import GuidelineService
from bs4 import BeautifulSoup

service = GuidelineService()

guideline_list = service.download_guideline_list()

current_chapter_level = -1
current_chapter_list = ["", "", ""]
current_chapter = ""

out_csv = "Leitlinie|Kapitel|Text|Typ\n"

def scan_subsections(subsection_list):
    global out_csv, current_chapter_list, current_chapter_level, current_chapter
    current_chapter_level += 1

    for subsection in subsection_list:
        if subsection['type'] == "ChapterCT":
            if current_chapter_level < len(current_chapter_list):
                soup = BeautifulSoup(subsection['title'])
                current_chapter_list[current_chapter_level] = soup.get_text()
                current_chapter = soup.get_text()
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

            reco = [guideline['short_title'], current_chapter, reco_text, "Empfehlung"]
            out_csv += "|".join(reco)+"\n"
        elif subsection['type'] == "TextCT":
            soup = BeautifulSoup(subsection['text'], features="lxml")
            reco_text = soup.get_text().replace("\r\n", "").replace("\r", "").replace("\n", "").strip()
            reco = [guideline['short_title'], current_chapter, reco_text, "Hintergrund"]
            out_csv += "|".join(reco)+"\n"
        if "subsections" in subsection:
            try:
                scan_subsections(subsection['subsections'])
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")

    current_chapter_level -= 1

guideline_id = "komplementaermedizin-in-der-behandlung-von-onkologischen-patientinnen"

guideline = service.download_guideline(guideline_id, guideline_state="private", load_references=False)
scan_subsections(guideline['subsections'])
f = open("%s_textlist.csv" % guideline['short_title'], "w")
f.write(out_csv)
f.close()
print(guideline['short_title']+" fertig.")