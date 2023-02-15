from docx import Document
from PllUnderstandability.IgnorableChapterConstructor import IgnorableChapterConstructor
import nltk
from HanTa import HanoverTagger as ht
tagger = ht.HanoverTagger("morphmodel_ger.pgz")
class PllWordFileParser:
    def __init__(self):
        self.ignorable_chapter_list = IgnorableChapterConstructor().ignorable_chapter_list
        self.ignorable_chapter_list.append('Starke und schwache Empfehlungen')
        self.ignorable_chapter_list.append('Medizinische Fachgesellschaften, Institutionen und Patientenvertreterinnen')
        self.ignorable_chapter_list.append('Was ist Palliativmedizin?')
        self.ignorable_chapter_list.append('Beratung bei sozialen Fragen')
        self.ignorable_chapter_list.append('Unterstützende Behandlung (Supportivmedizin)')
        self.ignorable_chapter_list.append('Ihre Rechte als Patientin')
        self.ignorable_chapter_list.append('Nachsorge')
        self.ignorable_chapter_list.append('Rehabilitation')
        self.ignorable_chapter_list.append('Entlassmanagement - Sozialleistungen – materielle Unterstützung')
        self.ignorable_chapter_list.append('Das können Sie selbst tun')
        self.ignorable_chapter_list.append('Krebs – Was ist das?')

        self.document = None
        self.forbidden_style_list = ["Title", "PLL Inhaltsverzeichnis"]

    def get_chapter_level(self, style_name):
        if "Head" in style_name and style_name.index("Head") == 0:
            level = style_name[-1]
            return int(level)
        else:
            return -1

    def text_has_verb(self, text):
        sents = nltk.sent_tokenize(text)
        for sent in sents:
            tokens = nltk.word_tokenize(sent, language="german")
            test = tagger.tag_sent(tokens)
            any_verb = any(filter(lambda x: "VA" in x[-1] or "VV" in x[-1], test))
            if any_verb:
                return True

        return False

    def Parse(self, word_file_path: Document):
        paragraph_dict = {}
        current_chaptername = ""
        self.document = Document(word_file_path)
        for paragraph in self.document.paragraphs:
            if paragraph.style.name in self.forbidden_style_list:
                continue

            if "Head" in paragraph.style.name and paragraph.style.name.index("Head") == 0:
                current_chaptername = paragraph.text.strip().replace(".", "")

            in_relevant_chapter = not any(x.strip() in current_chaptername for x in self.ignorable_chapter_list) and current_chaptername not in self.ignorable_chapter_list

            if not in_relevant_chapter or len(current_chaptername) == 0:
                continue

            if paragraph.style.name == "Normal":
                if not self.text_has_verb(paragraph.text):
                    continue

                if current_chaptername not in paragraph_dict:
                    paragraph_dict[current_chaptername] = []
                paragraph_dict[current_chaptername].append(paragraph.text)

        return paragraph_dict
