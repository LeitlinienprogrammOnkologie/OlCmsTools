from GuidelineService import GuidelineService
from html2text import HTML2Text

class ContentFinder:
    def __init__(self):
        self.current_chapter_level = 0
        self.current_chapter_nr = [3]
        self.current_chapter_name = ""
        self.current_guideline_title = ""
        self.html2text = HTML2Text()
        self.hit_counter = 0
        self.service = GuidelineService()
        self.out_str = "Leitlinie|Kapitelnr|Kapitelname|Inhaltstyp|Schlüsselwörter|Text|Empfehlungs-Nr\n"

    def Find(self, keyword_list):
        self.keyword_list = keyword_list
        guideline_list = self.service.download_guideline_list()

        for guideline in guideline_list:
            if guideline['guideline_language']['id'] == "de":
                self.FindInGuideline(guideline)
                print("%s: %s" % (guideline['short_title'], self.hit_counter))

        with open("results.csv", "w", encoding="utf-8") as f:
            f.write(self.out_str)

    def FindInGuideline(self, guideline):
        self.hit_counter = 0
        self.current_chapter_level = 0
        self.current_chapter_nr = [2]
        self.current_chapter_name = ""
        self.current_guideline_title = guideline['short_title']

        guideline = self.service.download_guideline(guideline['id'], 'published')

        for subsection in guideline['subsections']:
            self.FindInSubsection(subsection)

    def FindInSubsection(self, subsection):
        if subsection['type'] == "ChapterCT":
            if len(self.current_chapter_nr) <= self.current_chapter_level:
                self.current_chapter_nr.append(0)
            self.current_chapter_name = subsection['title']
            self.current_chapter_nr[self.current_chapter_level] += 1
            pass

        if (subsection['type'] == "TextCT" or subsection['type'] == "RecommendationCT") and 'text' in subsection:
            if subsection['type'] == "TextCT":
                type = "Hintergrundtext"
                reco_nr = subsection['number'].replace(".","_")
            else:
                type = "Empfehlung"
                reco_nr = ""
            html_text = subsection['text']
            text = self.html2text.handle(html_text).replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("|", " ").replace("  ", " ")

            hit_list = []
            for keyword in self.keyword_list:
                if keyword in text and keyword not in hit_list:
                    hit_list.append(keyword)

            if len(hit_list) > 0:
                self.hit_counter += len(hit_list)
                self.out_str += "%s|%s|%s|%s|%s|%s|%s\n" % (self.current_guideline_title, "_".join([str(x) for x in self.current_chapter_nr if x > 0]), self.current_chapter_name, type,
                ",".join(hit_list), text, reco_nr)


        for subsubsection in subsection['subsections']:
            self.FindInSubsection(subsubsection)

        for i in range(0, len(self.current_chapter_nr)):
            if i >= self.current_chapter_level:
                self.current_chapter_nr.pop()
        self.current_chapter_level -= 1






