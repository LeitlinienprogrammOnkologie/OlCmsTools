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

    def FindByGuidelineHierarchy(self, keyword_list):
        self.keyword_list = keyword_list

        guideline_list = self.service.download_guideline_list("consulted")
        guideline_list = [x for x in guideline_list if x['guideline_language']['id'] == 'de']

        buffer = self.service.download_guideline_list("private")
        for guideline in [x for x in buffer if x['guideline_language']['id'] == 'de']:
            if not any([x for x in guideline_list if x['id'] == guideline['id']]):
                guideline_list.append(guideline)
            else:
                pass

        buffer = self.service.download_guideline_list("published")
        for guideline in [x for x in buffer if x['guideline_language']['id'] == 'de']:
            if not any([x for x in guideline_list if x['id'] == guideline['id']]):
                guideline_list.append(guideline)
            else:
                pass

        for guideline in guideline_list:
            self.FindInGuideline(guideline)
            print("%s: %s" % (guideline['short_title'], self.hit_counter))

        with open("results.csv", "w", encoding="utf-8") as f:
            f.write(self.out_str)

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
        self.current_chapter_level = -1
        self.current_chapter_nr = [2]
        self.current_chapter_name = ""
        self.current_guideline_title = guideline['short_title']
        self.current_guideline_state = guideline['state']

        guideline = self.service.download_guideline(guideline['id'], guideline_state=guideline['state'])

        for subsection in guideline['subsections']:
            self.FindInSubsection(subsection)

    def AddWholeChapter(self, keyword, subsection):
        if subsection['type'] == "TextCT":
            type = "Hintergrundtext"
        elif subsection['type'] == "RecommendationCT":
            type = "Empfehlung"
        elif subsection['type'] == "TableCT":
            type = "Tabelle"
        else:
            type = ""

        if len(type) > 0:
            self.hit_counter += 1
            html_text = subsection['text']
            text = self.html2text.handle(html_text).replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("|"," ").replace("  ", " ")
            self.out_str += "%s|%s|%s|%s|%s|%s|%s|%s\n" % (self.current_guideline_title, self.current_guideline_state, "_".join([str(x) for x in self.current_chapter_nr if x > 0]), self.current_chapter_name, type, keyword, text, type)

        for subsubsection in subsection['subsections']:
            self.AddWholeChapter(keyword, subsubsection)

    def FindInSubsection(self, subsection):
        if subsection['type'] == "ChapterCT":
            self.current_chapter_level += 1
            if len(self.current_chapter_nr) <= self.current_chapter_level:
                self.current_chapter_nr.append(0)
            self.current_chapter_name = subsection['title']
            self.current_chapter_nr[self.current_chapter_level] += 1

            for keyword in self.keyword_list:
                if keyword in subsection['title']:
                    print(subsection['title'])
                    self.AddWholeChapter(keyword, subsection)
        else:
            if (subsection['type'] == "TextCT" or subsection['type'] == "RecommendationCT") and 'text' in subsection:
                if subsection['type'] == "TextCT":
                    type = "Hintergrundtext"
                    reco_nr = ""
                else:
                    type = "Empfehlung"
                    reco_nr = subsection['number'].replace(".","_")
                html_text = subsection['text']
                text = self.html2text.handle(html_text).replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("|", " ").replace("  ", " ")

                hit_list = []
                for keyword in self.keyword_list:
                    if keyword in text and keyword not in hit_list:
                        hit_list.append(keyword)

                if len(hit_list) > 0:
                    self.hit_counter += len(hit_list)
                    self.out_str += "%s|%s|%s|%s|%s|%s|%s|%s\n" % (self.current_guideline_title, self.current_guideline_state, "_".join([str(x) for x in self.current_chapter_nr if x > 0]), self.current_chapter_name, type,
                    ",".join(hit_list), text, reco_nr)

        for subsubsection in subsection['subsections']:
            self.FindInSubsection(subsubsection)

        if subsection['type'] == "ChapterCT":
            for i in range(0, len(self.current_chapter_nr)):
                if i >= self.current_chapter_level:
                    self.current_chapter_nr.pop()
            self.current_chapter_level -= 1