from docx import Document
class BrWordFileParser:
    def __init__(self):
        self.document = None
        self.forbidden_chaptername_list = [
            "VORWORT",
            "REHABILITATION UND NACHSORGE",
            'HIER ERHALTEN SIE',
            'INFORMATIONEN UND RAT',
            'ERKLÄRUNG VON FACHAUSDRÜCKEN',
            'QUELLENANGABE',
            'ANHANG',
        ]

    def get_chapter_level(self, style_name):
        level = style_name[-1]
        return int(level)

    def Parse(self, word_file_path: Document):
        paragraph_dict = {}
        self.document = Document(word_file_path)
        current_chaptername = ""
        for paragraph in self.document.paragraphs:
            if len(paragraph.text.strip()) == 0:
                continue
            if "H1" in paragraph.style.name and paragraph.style.name.index("H1") == 0:
                current_chaptername = paragraph.text.replace("\n", " ").replace("\r", " ").replace("  ", " ").strip()
                pass
            if current_chaptername.strip().upper() in self.forbidden_chaptername_list:
                continue
            if len(current_chaptername) == 0:
                continue

            if paragraph.style.name == "Normal" or "Fließ" in paragraph.style.name:
                if current_chaptername not in paragraph_dict:
                    paragraph_dict[current_chaptername] = []
                paragraph_dict[current_chaptername].append(paragraph.text)

        return paragraph_dict
