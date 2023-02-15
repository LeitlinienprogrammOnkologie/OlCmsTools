from docx import Document
class IgnorableChapterConstructor:
    def __init__(self):
        self.ignorable_chapter_list = []
        document = Document("./PllUnderstandability/Patientenleitlinien_Template_ÜS.docx")
        for paragraph in document.paragraphs:
            if ("Normal" in paragraph.style.name or "Head" in paragraph.style.name) and len(paragraph.text.strip()) > 0:
                self.ignorable_chapter_list.append(paragraph.text.strip())
                if "Patienten" in paragraph.text:
                    self.ignorable_chapter_list.append(paragraph.text.strip().replace("Patienten", "Patientinnen"))
                elif "Patient" in paragraph.text:
                    self.ignorable_chapter_list.append(paragraph.text.strip().replace("Patient", "Patientin"))

                if "Broschüre" in paragraph.text:
                    self.ignorable_chapter_list.append(paragraph.text.strip().replace("Broschüre", "Patientenleitlinie"))
                    self.ignorable_chapter_list.append(paragraph.text.strip().replace("Broschüre", "Patientinnenleitlinie"))
