from docx import Document
class S3WordFileParser:
    def __init__(self):
        self.document = None
        self.forbidden_style_list = ["Title", "PLL Inhaltsverzeichnis"]
        self.forbidden_chaptername_list = [
            'Informationen zu dieser Leitlinie',
        ]

    def get_chapter_level(self, style_name):
        level = style_name[-1]
        return int(level)

    def Parse(self, word_file_path: Document):
        paragraph_dict = {}
        self.document = Document(word_file_path)
        current_chaptername = ""
        current_forbidden_level = 10000
        for paragraph in self.document.paragraphs:
            if paragraph.style.name in self.forbidden_style_list or len(paragraph.text.strip()) == 0:
                continue
            if "Heading" in paragraph.style.name and paragraph.style.name.index("Heading") == 0:
                if current_forbidden_level < self.get_chapter_level(paragraph.style.name):
                    continue
                current_chaptername = paragraph.text
                current_forbidden_level = self.get_chapter_level(paragraph.style.name)
                pass
            if current_chaptername in self.forbidden_chaptername_list:
                continue
            if len(current_chaptername) == 0:
                continue

            #print(paragraph.style.name)

            if "Normal" in paragraph.style.name:
                if current_chaptername not in paragraph_dict:
                    paragraph_dict[current_chaptername] = []
                paragraph_dict[current_chaptername].append(paragraph.text)

        return paragraph_dict
